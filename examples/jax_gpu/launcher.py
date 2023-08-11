#!/usr/bin/env python3
from absl import app
from absl import flags

from lxm3 import xm
from lxm3 import xm_cluster

_LAUNCH_ON_CLUSTER = flags.DEFINE_boolean(
    "launch_on_cluster", False, "Launch on cluster"
)
_GPU = flags.DEFINE_boolean("gpu", False, "If set, use GPU")
_SINGULARITY_CONTAINER = flags.DEFINE_string(
    "container", "jax-cuda.sif", "Path to singularity container"
)


def main(_):
    with xm_cluster.create_experiment(experiment_title="basic") as experiment:
        # It's actually not necessary to use a container, without it, we
        # fallback to the current python environment for local executor and
        # whatever Python environment picked up by the cluster for GridEngine.
        # For remote execution, using the host environment is not recommended.
        # as you may spend quite some time figuring out dependency problems than
        # writing a simple Dockfiler/Singularity file.
        singularity_container = _SINGULARITY_CONTAINER.value
        if _GPU.value:
            # Currently, the job requirements accept arbitrary key-value pairs
            # For SGE, this is translated to -l key=value directives.
            requirements = xm_cluster.JobRequirements(gpu=1, tmem=8 * xm.GB)
        else:
            # CS cluster suggests setting both tmem and h_vmem
            # for CPU jobs. For GPU jobs, only tmem is used and setting
            # h_vmem may result in an error.
            # The way to configure myriad is different.
            requirements = xm_cluster.JobRequirements(tmem=8 * xm.GB, h_vmem=8 * xm.GB)
        if _LAUNCH_ON_CLUSTER.value:
            # There are more configuration for GridEngine, checkout the source code.
            executor = xm_cluster.GridEngine(
                requirements=requirements,
                walltime=10 * xm.Min,
                singularity_container=singularity_container,
            )
        else:
            executor = xm_cluster.Local(
                requirements=requirements,
                singularity_container=singularity_container,
            )

        packageable = xm.Packageable(
            executable_spec=xm_cluster.PythonPackage(
                # This is a relative path to the launcher that contains
                # your python package (i.e. the directory that contains pyproject.toml)
                path=".",
                # Entrypoint is the python module that you would like to
                # In the implementation, this is translated to
                #   python3 -m py_package.main
                entrypoint=xm_cluster.ModuleName("py_package.main"),
            ),
            executor_spec=executor.Spec(),
        )

        [executable] = experiment.package([packageable])

        experiment.add(
            xm.Job(
                executable=executable,
                executor=executor,
                # You can pass additional arguments to your executable with args
                # This will be translated to `--seed 1`
                # Note for booleans we currently use the absl.flags convention
                # so {'gpu': False} will be translated to `--nogpu`
                args={"seed": 1},
                # You can customize environment_variables as well.
                env_vars={"XLA_PYTHON_CLIENT_PREALLOCATE": "false"},
            )
        )


if __name__ == "__main__":
    app.run(main)
