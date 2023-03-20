from setuptools import setup, find_packages

long_description = ""

setup(
    name             = "keentune-target",
    version          = "2.0.1",
    description      = "KeenTune target unit",
    url              = "https://gitee.com/anolis/keentune_target",
    license          = "MulanPSLv2",
    packages         = find_packages(),
    package_data     = {'target': ['target.conf']},
    python_requires  = '>=3.6',
    long_description = long_description,
    install_requires = ['tornado'],
    
    classifiers = [
        "Environment:: KeenTune",
        "IntendedAudience :: Information Technology",
        "IntendedAudience :: System Administrators",
        "License :: OSI Approved :: MulanPSLv2",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "ProgrammingLanguage :: Python"
    ],

    data_files  = [
        ("/etc/keentune/target", ["agent/target.conf"]),
        ("/etc/keentune/target/scripts", ["agent/scripts/cpu-partitioning.sh"]),
        ("/etc/keentune/target/scripts", ["agent/scripts/functions"]),
        ("/etc/keentune/target/scripts", ["agent/scripts/powersave.sh"]),
        ("/etc/keentune/target/scripts", ["agent/scripts/realtime.sh"]),
        ("/etc/keentune/target/scripts", ["agent/scripts/spindown-disk.sh"]),
        ("/etc/keentune/target/scripts", ["agent/scripts/tuned-pre-udev.sh"]),
        ("/etc/keentune/target/scripts", ["agent/scripts/erdma.sh"]),
    ],

    entry_points = {
        'console_scripts': ['keentune-target=agent.agent:main']
    }
)
