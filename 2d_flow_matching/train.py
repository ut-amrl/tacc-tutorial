#!/usr/bin/env python
import argparse
import os
import time
import warnings

import torch
from torch import nn, Tensor
import matplotlib.pyplot as plt
from matplotlib import cm

# flow_matching imports
from flow_matching.path.scheduler import CondOTScheduler
from flow_matching.path import AffineProbPath
from flow_matching.solver import Solver, ODESolver
from flow_matching.utils import ModelWrapper

# Suppress torch meshgrid warnings
warnings.filterwarnings("ignore", category=UserWarning, module='torch')


def inf_train_gen(batch_size: int = 200, device: str = "cpu"):
    """
    Generate training data.
    """
    x1 = torch.rand(batch_size, device=device) * 4 - 2
    x2_ = torch.rand(batch_size, device=device) - torch.randint(high=2, size=(batch_size,), device=device) * 2
    x2 = x2_ + (torch.floor(x1) % 2)
    data = 1.0 * torch.cat([x1[:, None], x2[:, None]], dim=1) / 0.45
    return data.float()


# --- Activation and Model definitions ---
class Swish(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x: Tensor) -> Tensor:
        return torch.sigmoid(x) * x


class MLP(nn.Module):
    def __init__(self, input_dim: int = 2, time_dim: int = 1, hidden_dim: int = 128):
        super().__init__()
        self.input_dim = input_dim
        self.time_dim = time_dim
        self.hidden_dim = hidden_dim
        self.main = nn.Sequential(
            nn.Linear(input_dim + time_dim, hidden_dim),
            Swish(),
            nn.Linear(hidden_dim, hidden_dim),
            Swish(),
            nn.Linear(hidden_dim, hidden_dim),
            Swish(),
            nn.Linear(hidden_dim, hidden_dim),
            Swish(),
            nn.Linear(hidden_dim, input_dim),
        )

    def forward(self, x: Tensor, t: Tensor) -> Tensor:
        sz = x.size()
        x = x.reshape(-1, self.input_dim)
        t = t.reshape(-1, self.time_dim).float()
        # Expand t if necessary to match x's shape
        t = t.reshape(-1, 1).expand(x.shape[0], 1)
        h = torch.cat([x, t], dim=1)
        output = self.main(h)
        return output.reshape(*sz)


class WrappedModel(ModelWrapper):
    def forward(self, x: torch.Tensor, t: torch.Tensor, **extras):
        return self.model(x, t)


def sample_and_visualize(vf, device, step_size, batch_size, num_time_points, output_path):
    """
    Samples trajectories using the trained model and visualizes them.
    The figure is saved to the output_path.
    """
    # Ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    # Wrap the trained model
    wrapped_vf = WrappedModel(vf)

    # Define sample times T and move to device
    T = torch.linspace(0, 1, num_time_points).to(device)

    # Generate initial data for ODE sampling
    x_init = torch.randn((batch_size, 2), dtype=torch.float32, device=device)

    # Create ODE solver and sample trajectories
    solver = ODESolver(velocity_model=wrapped_vf)
    sol = solver.sample(time_grid=T, x_init=x_init, method='midpoint',
                        step_size=step_size, return_intermediates=True)
    sol = sol.cpu().numpy()
    T_cpu = T.cpu()

    # Create subplots (one for each time point)
    fig, axs = plt.subplots(1, num_time_points, figsize=(20, 20))
    for i in range(num_time_points):
        H = axs[i].hist2d(sol[i, :, 0], sol[i, :, 1], 300, range=((-5, 5), (-5, 5)))
        cmin = 0.0
        cmax = torch.quantile(torch.from_numpy(H[0]), 0.99).item()
        norm = cm.colors.Normalize(vmax=cmax, vmin=cmin)
        _ = axs[i].hist2d(sol[i, :, 0], sol[i, :, 1], 300, range=((-5, 5), (-5, 5)), norm=norm)
        axs[i].set_aspect('equal')
        axs[i].axis('off')
        axs[i].set_title('t= %.2f' % (T_cpu[i]))
    plt.tight_layout()

    # Save the figure
    output_file = os.path.join(output_path, "flow_trajectories.png")
    plt.savefig(output_file)
    print(f"Visualization saved to {output_file}")
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Train velocity flow matching model")
    parser.add_argument("--lr", type=float, default=0.001,
                        help="Learning rate for optimizer")
    parser.add_argument("--batch_size", type=int, default=50000,
                        help="Batch size for training and ODE sampling")
    parser.add_argument("--step_size", type=float, default=0.05,
                        help="Step size for the ODE solver")
    parser.add_argument("--iterations", type=int, default=20001,
                        help="Number of training iterations")
    parser.add_argument("--print_every", type=int, default=2000,
                        help="Frequency of printing training info")
    parser.add_argument("--hidden_dim", type=int, default=512,
                        help="Hidden dimension of the MLP model")
    parser.add_argument("--num_time_points", type=int, default=10,
                        help="Number of time points for ODE sampling visualization")
    parser.add_argument("--output_dir", type=str, default="outputs",
                        help="Directory to store output images")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    args = parser.parse_args()

    # Set random seed for reproducibility
    torch.manual_seed(args.seed)

    # Select device
    if torch.cuda.is_available():
        device = 'cuda:0'
        print('Using gpu')
    else:
        device = 'cpu'
        print('Using cpu.')

    # --- Model Initialization ---
    vf = MLP(input_dim=2, time_dim=1, hidden_dim=args.hidden_dim).to(device)

    # --- Instantiate Path and Optimizer ---
    path = AffineProbPath(scheduler=CondOTScheduler())
    optimizer = torch.optim.Adam(vf.parameters(), lr=args.lr)

    # --- Training Loop ---
    print_every = args.print_every
    start_time = time.time()
    for i in range(args.iterations):
        optimizer.zero_grad()

        # Sample data: (x_0, x_1) pairs
        x_1 = inf_train_gen(batch_size=args.batch_size, device=device)
        x_0 = torch.randn_like(x_1).to(device)

        # Sample time uniformly for each data point
        t = torch.rand(x_1.shape[0]).to(device)

        # Generate a probability path sample using the affine path object
        path_sample = path.sample(t=t, x_0=x_0, x_1=x_1)

        # Compute flow matching L2 loss
        loss = torch.pow(vf(path_sample.x_t, path_sample.t) - path_sample.dx_t, 2).mean()

        loss.backward()
        optimizer.step()

        # Logging
        if (i + 1) % print_every == 0:
            elapsed = time.time() - start_time
            print('| iter {:6d} | {:5.2f} ms/step | loss {:8.3f}'.format(
                i + 1, elapsed * 1000 / print_every, loss.item()))
            start_time = time.time()

    # --- Post-Training: Sampling & Visualization ---
    # Create a subdirectory name by concatenating key parameters
    param_str = (f"lr_{args.lr}_bs_{args.batch_size}_step_{args.step_size}_"
                 f"hidden_{args.hidden_dim}_iter_{args.iterations}_ntp_{args.num_time_points}")
    output_path = os.path.join(args.output_dir, param_str)
    sample_and_visualize(vf, device, args.step_size, args.batch_size, args.num_time_points, output_path)


if __name__ == '__main__':
    main()
