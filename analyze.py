#!/usr/bin/env python3

import os
import math

class Remote:
    def __init__(self, name):
        self.name = name
        self.projects = {}

    def add_project(self, project):
        self.projects[project.name] = project

    def replications(self):
        result = []
        for name, project in self.projects.items():
            for sha1, rep in project.replications.items():
                if self.name in rep:
                    result.append(rep[self.name])
        return result

class Project:
    def __init__(self, name):
        self.name = name
        self.replications = {}

    def add_replication(self, remote, replication):
        if not replication.sha1 in self.replications:
            self.replications[replication.sha1] = {}

        self.replications[replication.sha1][remote.name] = replication

class Replication:
    def __init__(self, sha1, timestamp, delay, project, remote):
        self.sha1 = sha1
        self.timestamp = timestamp
        self.delay = delay
        self.project = project
        self.remote = remote

remotes = {}
projects = {}
replications = []

# Load results
for remote_name in os.listdir("results"):

    remote = Remote(remote_name)
    remotes[remote_name] = remote

    for project_name in os.listdir("results/" + remote_name):
        if not project_name in projects:
            project = Project(project_name)
            projects[project_name] = project
        else:
            project = projects[project_name]

        remote.add_project(project)

        file_path = os.path.join("results", remote_name, project_name)

        f = open(file_path)

        for line in f:
            info = line.rstrip().split(' ')
            replication = Replication( info[2], int(info[0]), int(info[1]), project, remote)
            project.add_replication(remote, replication)
            replications.append(replication)

        f.close()


print("Per remote ...")
for name, remote in remotes.items():
    replications = remote.replications()
    print("\n%s: %d replications" % (name, len(replications)))

    if len(replications) == 0:
        next

    # Average
    avg_sum = 0
    for rep in replications:
        avg_sum += rep.delay
    avg_sum = avg_sum / len(replications)

    print("\t -> Average delay = %d ms" % avg_sum)

    # Slow
    slow_limit = 2 * avg_sum

    print("\t -> Slow ones (> 2*average)")
    for rep in replications:
        if rep.delay > slow_limit:
            print("\t\t%s: %s %d" % (rep.project.name, rep.sha1, rep.delay))

    # Distribution

    distrib = {}
    delta = 5000

    for rep in replications:
        nb = math.floor(rep.delay / delta)
        if not nb in distrib:
            distrib[nb] = [ rep ]
        else:
            distrib[nb].append(rep)

    print("\t -> Distribution")
    cumul = 0
    for nb in sorted(distrib.keys()):
        cumul += len(distrib[nb])
        print("\t\t[%8d, %8d[: %4d (%.1f %%)" % (nb*delta, (nb+1)*delta, len(distrib[nb]), (cumul*100/len(replications)) ) )

