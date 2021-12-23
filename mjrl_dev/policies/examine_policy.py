from os import environ
environ["MKL_THREADING_LAYER"] = "GNU"
import pickle
import os

# Utilities
import evaluate_args
from mjrl.utils.gym_env import GymEnv

# Policies
from mjrl.policies.gaussian_mlp import MLP
import time

# Samplers
# import mjrl.samplers.trajectory_sampler as trajectory_sampler
# import mjrl.samplers.base_sampler as base_sampler
from mjrl.samplers.core import do_rollout
from mjrl_dev.utils.viz_paths import plot_horizon_distribution, plot_paths
import numpy as np
import mj_envs

def main():
    # See evaluate_args.py for the list of args.
    args = evaluate_args.get_args()

    if args.include is not "":
        exec("import "+args.include)

    if args.env_name is "":
        print(
            "Unknown env. Use 'python examine_policy --help' for instructions")
        return

    # load envs
    # adept_envs.global_config.set_config(
    #     args.env_name, {
    #         'robot_params': {
    #             'is_hardware': args.hardware,
    #             'legacy': args.legacy,
    #             'device_name': args.device,
    #             'overlay': args.overlay,
    #             'calibration_mode': args.calibration_mode,
    #         },
    #     })
    e = GymEnv(args.env_name)
    e.env.env.seed(args.seed)

    # load policy
    policy = args.policy
    mode = args.mode
    if args.policy == "":
        pol = MLP(e.spec, init_log_std=args.log_std)
        print(args.log_std)
        mode = "exploration"
        policy = "random_policy.pickle"
    elif args.policy == "saved":
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        policy = curr_dir + "/" + args.env_name + "/best_policy.pickle"
        pol = pickle.load(open(policy, 'rb'))
    else:
        # do this on the remote machine ============
        # weights = pol.get_param_values()
        # pickle.dump(weights, open("weights.pickle", 'wb'))
        # on local machine ============
        # pol = MLP(e.spec, init_log_std=-3.50)
        # loaded_params = pickle.load(open("weights.pickle", 'rb'))
        # pol.set_param_values(loaded_params)
        # pickle.dump(pol, open(policy, 'wb')) # save the policy
        pol = pickle.load(open(policy, 'rb'))
        if mode == "exploration":
            # pol.log_std = pol.log_std + args.log_std
            print(pol.log_std_val)
            pol.log_std_val = pol.log_std_val + args.log_std

    print(pol.log_std_val)

    # dump rollouts
    if (args.num_samples > 0):
        # if (mode == "evaluation"):
            # pol.log_std = pol.log_std - 10  # since there is no other way of expecifying that we want mean policy samplling

        # parallel sampling
        # paths = trajectory_sampler.sample_paths_parallel(num_samples, pol, e.horizon, env_name, 0, 1)

        # Serial sampling
        paths = do_rollout(
            num_traj=args.num_samples,
            env=e,
            policy=pol,
            eval_mode = (mode=='evaluation'),
            horizon=e.horizon,
            base_seed=args.seed)

        # Policy stats
        eval_success = e.env.env.evaluate_success(paths)
        # try:
        #     eval_rewards = np.mean([np.sum(p['env_infos']['reward']) for p in paths])/e.horizon
        #     eval_score = np.mean([np.mean(p['env_infos']['score']) for p in paths])
        # except:
        #     eval_rewards = np.mean([np.sum(p['env_infos']['rwd_dense']) for p in paths])/e.horizon
        #     eval_score = np.mean([np.mean(p['env_infos']['rwd_sparse']) for p in paths])

        # evaluate_success = np.mean([np.sum(p['env_infos']['solved']) for p in paths])

        # stats = "Policy stats:: <mean reward/step: %+.3f>, <mean score/step: %+.3f>, <mean success: %2.1f%%>\n" % (
        #     eval_rewards, eval_score, eval_success)
        # for ipath, path in enumerate(paths):
        #     stats = stats + "path%d:: <reward[-1]: %+.3f>, <score[-1]: %+.3f>\n" % (
        #         ipath, path['env_infos']['rwd_dense'][-1], path['env_infos']['rwd_sparse'][-1])
        # print(stats)

        print("eval_success: ", eval_success)
        # save to a file
        time_stamp = time.strftime("%Y%m%d-%H%M%S")
        # file_name = policy[:-7] + '_stats_{}.txt'.format(time_stamp)
        # print(stats, file=open(file_name, 'w'))
        # print("saved ", file_name)

        # plot_horizon_distribution(paths, e, fileName_prefix=policy[:-7])
        plot_paths(paths, e, fileName_prefix=policy[:-7])
        # file_name = policy[:-7] + '_paths_{}.pickle'.format(time_stamp)
        # pickle.dump(paths, open(file_name, 'wb'))
        # print("saved ", file_name)

    else:
        print
        # Visualized policy
        if args.render == "onscreen":
            # On screen
            e.env.env.visualize_policy(
                pol,
                horizon=e.horizon,
                num_episodes=args.num_episodes,
                mode=mode)
        else:
            # Offscreen buffer
            e.env.env.visualize_policy_offscreen(
                pol,
                horizon=e.horizon,
                num_episodes=args.num_episodes,
                mode=mode,
                filename=args.filename)

    # Close envs
    # e.env.env.close_env()


if __name__ == '__main__':
    main()
