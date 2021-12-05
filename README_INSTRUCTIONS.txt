Requirements:
- Python 3.9
    Modules:
        - Pillow
        - svg.path
        - svgwrite
        - networkx
        - numpy
        - matplotlib

The simulator can be run by just running:

"python GUI.py weather_refresh_interval time_spent_at_node experimentX"

Arguments:
    weather_refresh_interval - MANDATORY argument - MUST BE >=1 - time in seconds between weather changes, in practice a large number can be set to have a fixed weather that doesn't cause algorithm reruns due to weather changes

    time_spent_at_node - MANDATORY argument - MUST BE >=1 - time in seconds (recommended 180) for how much the glider will stay in each node (effectively a boost to all uplift values)

    experimentX - OPTIONAL argument - which experiment to run, valid options are 'experiment1', 'experiment2' and 'experiment3', this parameter effectively specifies which weather data json to use so to fully replicate the experiments from the report the other two parameters needs to be replicated too (as shown in examples below)

Examples:
    - "python GUI.py 5 180" - configuration that demonstrates pretty well

    - "python GUI.py 10000 180 experiment1" - configuration used for Experiment 1

    - "python GUI.py 10000 200 experiment2" - configuration used for Experiment 2
    - "python GUI.py 10000 300 experiment2" - configuration used for Experiment 2
    - "python GUI.py 10000 400 experiment2" - configuration used for Experiment 2

    - "python GUI.py 10000 180 experiment3" - configuration used for Experiment 3
    - "python GUI.py 30 180 experiment3" - configuration used for Experiment 3

GENERAL USE:

- The starting position is indicated by the glider icon on the map portion of the GUI.
- Left mouse click anywhere on the map sets the desired destination position (specific coordinates indicated on the right in the input fields).
- Both positions can also be specifically set from the input fields.
- Starting and destination altitudes are only set through the input fields.

- When all desired parameters are set, clicking the "Run Navigation" button starts the algorithm with the current parameters. The algorithm will be rerun with the last submitted parameters whenever a weather change occurs (usually indicated by changed blue vector field). This can sometimes take a bit of time during which the program will appear to be frozen but it is not.

- RESULTS - the results of each algorithm run can be seen in text format in the generated results.log file located in the main project folder (./MBSEF21/results.log), this file is dynamically updated so it can be viewed in parallel with the graphical interface (depending on the program used to view it, it may need to be manually refreshed/reopened though)
