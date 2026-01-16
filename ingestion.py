import os
import git
def cloning(git_link):
    repo_name = git_link.split("/")[-1].replace(".git", "")
    if not os.path.exists("cloned_files/" + repo_name):
        git.Repo.clone_from(git_link, "cloned_files/" + repo_name)
    return repo_name
if __name__ == "__main__":
    cloning("https://github.com/ManushreeBartaria/TrickIT.git")