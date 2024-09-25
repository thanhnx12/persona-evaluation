# import matplotlib.pyplot as plt
# import numpy as np

# # Example scores dictionary (you should provide your own scores)
# # scores_base = {'tone': 5.32,
# #              'wording': 4.10,
# #              'emotional_expression': 5.66,
# #              'behavior_alignment': 7.27}

# # scores = {'tone' : 5.58,
# #             'wording': 4.99,
# #         'emotional_expression' : 5.566666666666666,
# #         'behavior_alignment' : 7.0}


# # scores = {'tone': 5.340425531914893,
# #         'wording': 4.0,
# #         'emotional_expression': 5.48936170212766,
# #          'behavior_alignment': 5.382978723404255}


# # eval result on 20 persona
# # llama31
# scores_base = {'tone': 5.380710659898477, 'wording': 4.715736040609137, 'emotional_expression': 5.593908629441624, 'behavior_alignment': 5.934010152284264}
# #ours
# scores = {'tone': 4.604060913705584, 'wording': 4.020304568527918, 'emotional_expression': 4.593908629441624, 'behavior_alignment': 4.8578680203045685}

# scores = {'tone': 6.946428571428571, 'wording': 6.885245901639344, 'emotional_expression': 7.508474576271187, 'behavior_alignment': 7.396551724137931}
# scores_base = {'tone': 8.033333333333333, 'wording': 7.721311475409836, 'emotional_expression': 8.133333333333333, 'behavior_alignment': 8.192982456140351}


# categories = list(scores.keys())
# values = list(scores.values())
# values_base = list(scores_base.values())
# max_value = 10
# N = len(categories)

# angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
# values += values[:1]
# values_base += values_base[:1]
# angles += angles[:1]

# # Increase figure size
# plt.figure(figsize=(12, 8))
# fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'polar': True})

# # Set background color
# fig.patch.set_facecolor('#f0f0f0')
# ax.set_facecolor('#ffffff')

# # Plot grid lines
# ax.grid(color='gray', linestyle='--', alpha=0.7)

# # Plot and fill the data for both models
# ax.plot(angles, values, color='#3498db', linewidth=2, label='SFT model ver 2')
# ax.fill(angles, values, color='#3498db', alpha=0.25)
# ax.plot(angles, values_base, color='#e74c3c', linewidth=2, label='Meta-Llama-3.1-8B-Instruct-Turbo')
# ax.fill(angles, values_base, color='#e74c3c', alpha=0.25)

# # Customize ticks and labels
# plt.xticks(angles[:-1], categories, color='#2c3e50', size=12, fontweight='bold')
# ax.set_rlabel_position(0)
# plt.yticks(np.arange(2, max_value + 1, 2), color='#2c3e50', size=10)
# ax.set_ylim(0, max_value)

# # Add a title and legend
# plt.title('Evaluation Scores Comparison', size=20, color='#2c3e50', fontweight='bold', y=1.1)
# plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)

# # Add subtle animation effect
# for i in range(100):
#     ax.set_ylim(0, max_value * (i + 1) / 100)
#     plt.pause(0.01)

# plt.tight_layout()
# plt.show()


import matplotlib.pyplot as plt
import numpy as np

def plot_radar(scores_dict, max_value=10, figsize=(12, 8)):
    categories = list(scores_dict[list(scores_dict.keys())[0]].keys())
    N = len(categories)

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'polar': True})

    # Set background color
    fig.patch.set_facecolor('#f0f0f0')
    ax.set_facecolor('#ffffff')

    # Plot grid lines
    ax.grid(color='gray', linestyle='--', alpha=0.7)

    # Color palette
    colors = plt.cm.get_cmap('Set2')(np.linspace(0, 1, len(scores_dict)))

    for i, (model, scores) in enumerate(scores_dict.items()):
        values = list(scores.values())
        values += values[:1]
        ax.plot(angles, values, linewidth=2, label=model, color=colors[i], marker='o')

    # Customize ticks and labels
    plt.xticks(angles[:-1], categories, color='#2c3e50', size=12, fontweight='bold')
    ax.set_rlabel_position(0)
    plt.yticks(np.arange(2, max_value + 1, 2), color='#2c3e50', size=10)
    ax.set_ylim(0, max_value)

    # Add a title and legend
    plt.title('Evaluation Scores Comparison', size=20, color='#2c3e50', fontweight='bold', y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)

    plt.tight_layout()
    plt.show()


# Example usage
scores_dict = {
    'Meta-Llama-3.1-8B-Instruct-Turbo': {
        'tone': 8.033,
        'wording': 7.721,
        'emotional_expression': 8.133,
        'behavior_alignment': 8.193
    },
    'SFT model ver 2': {
        'tone': 6.946,
        'wording': 6.885,
        'emotional_expression': 7.508,
        'behavior_alignment': 7.397
    },
    # You can add more models here
    'Gemma2 - 9B': {'tone': 7.785340314136126, 'wording': 7.71505376344086, 'emotional_expression': 7.916666666666667, 'behavior_alignment': 8.031746031746032}
}

plot_radar(scores_dict)