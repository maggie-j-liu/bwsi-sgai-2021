import os
import pandas as pd
import matplotlib


# import matplotlib.pyplot as plt
# Set up environment for plotting (needed on my machine; usually you can just the commented import and be fine)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
gui_env = ['TKAgg', 'Qt5Agg']
for gui in gui_env:
    try:
        matplotlib.use(gui, force=True)
        from matplotlib import pyplot as plt
        break
    except:
        continue

# Let's load the log file into a dataframe
training_results_log = 'rl-agent-test_training.json'
training_results_df = pd.read_json(training_results_log)
print(training_results_df)

# Let's make a simple plot of reward over time (training step)
training_results_df.plot(x='nb_steps', y='episode_reward')
plt.savefig('basic_training_plot.png', dpi=300)
plt.show()
plt.close()
