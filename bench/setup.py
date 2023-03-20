from setuptools import setup, find_packages

long_description = ""

setup(
    name             = "keentune-bench",
    version          = "2.0.0",
    description      = "KeenTune bench unit",
    url              = "https://gitee.com/anolis/keentune_bench",
    license          = "MulanPSLv2",
    packages         = find_packages(),
    package_data     = {'bench': ['bench.conf']},
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
        ("/etc/keentune/bench", ["bench/bench.conf"]),
    ],

    entry_points = {
        'console_scripts': ['keentune-bench=bench.bench:main']
    }
)
