import sys
import gromacs_bjasync
import argparse

if __name__ == "__main__":

    usage = 'usage: %prog --config [--checkenv, --testjob, --workload, --help]'
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",help = "The resource configuration file")
    parser.add_argument("--checkenv",action="store_true",help = "Submit a job to test the remote environment")
    parser.add_argument("--testjob",action="store_true",help = "Submit a job to execute a simple gromacs ensemble")
    parser.add_argument("-w","--workload",action="store_true",help = "Performs tasks mentioned in the workload file")

    args = parser.parse_args()

    if args.config is None:
        parser.error("Please define a config file.")
    
    else:
        config = __import__(args.config.split(".")[0])

        from config import RESOURCE

        #One object per Remote Host
        obj1=gromacs_bjasync.simple()

        #Resource started at the Remote Host as defined by RESOURCE
        obj1.startResource(resource_info=RESOURCE)

        if args.checkenv is True:
            #Run test job to check environment
            result=obj1.checkEnv()
            sys.exit(result)

        elif args.testjob is True:
            #Run test job to submit a simple gromacs task
            result=obj1.startTestJob()
            sys.exit(result)

        elif args.workload is True:
            #Tasks started at the Remote Host as defined by TASK
            from config import TASK
            result=obj1.startTasks(task_info=TASK)
            print (result)
            sys.exit(0)

        else:
            print('Please enter a valid parameter (--checkenv, --testjob, --workload, --h for help)')
    
