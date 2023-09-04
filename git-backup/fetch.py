import os, sys, json, traceback, codecs, subprocess
from pathlib import Path
import urllib.request
import bs4 as bs

backupsDir = Path("backups")
tempDir = Path("temp")

supportedSites = ["https://github.com", "https://gitlab.com", "https://bitbucket.org"]
supportedSites = [ url.strip("/") for url in supportedSites ]

isTrue = lambda s : s.lower() in ["true", "yes", "y", "1"]

def extractRefs(path):
	with codecs.open(path, "r", "utf-8") as file:
		soup = bs.BeautifulSoup(file, "html.parser")
		# print(soup.prettify())
		return sorted(set([ a["href"] for a in soup.find_all("a", href=True) ]))

def gitFetchingURL(ref, siteURL):
	return siteURL + "/" + ref + ".git"

# ignoreCache: do requests and override html or json cached files.
def fetchContent(url, path, ignoreCache=False):
	if not ignoreCache and path.is_file() and path.stat().st_size > 0:
		print("Loading:", path)
	else:
		print("Fetching:", url)
		urllib.request.urlretrieve(url, path)

# ignoreCache: remove cached repositories and clone from scratch.
def saveRepos(repos, dirName, username, onlyLastCommit=False, ignoreCache=False):
	path = backupsDir / username / dirName
	for url in repos:
		subprocess.call(["sh", "./clone-pull.sh", str(path), url, str(int(onlyLastCommit)), str(int(ignoreCache))])

def backup(url, saveStarred=False, onlyLastCommit=False, ignoreCache=False):
	username, repositories, starred = "", [], []
	try:
		os.makedirs(tempDir, exist_ok=True)
		check = [ siteURL in url for siteURL in supportedSites ]
		assert True in check, "Unsupported URL: " + url
		siteURL = supportedSites[check.index(True)]
		site = siteURL.split("/")[2]
		username = url.split(siteURL)[1].split("/")[1].lower()
		assert username != ""
		print("Found user:", username)

		if site == "github.com":
			pages = ["repositories"] + (["stars"] if saveStarred else [])
			for page in pages:
				path = tempDir / (site + "-" + username + "-" + page + ".html")
				url = siteURL + "/" + username + "?tab=" + page
				fetchContent(url, path, ignoreCache)
				refs = extractRefs(path)
				for ref in refs:
					if page == "repositories" and username + "/" in ref.lower() and not (
						"stargazers" in ref or "forks" in ref):
						repositories.append(gitFetchingURL(ref, siteURL))
					elif page == "stars" and "stargazers" in ref: # "stargazers" or "forks"
						ref = ref.replace("/" + "stargazers", "")
						starred.append(gitFetchingURL(ref, siteURL))

		elif site == "gitlab.com":
			path = tempDir / (site + "-" + username + ".json")
			url = siteURL + "/groups/" + username + "/-/children.json"
			fetchContent(url, path, ignoreCache)
			with open(path, "r") as jsonContent:
				jsonDict = json.load(jsonContent)
				repositories = sorted([ gitFetchingURL(obj["relative_path"], siteURL) for obj in jsonDict ])
				starred = [] # not accessible without a boring token

		elif site == "bitbucket.org":
			path = tempDir / (site + "-" + username + ".json")
			url = siteURL + "/api/2.0/repositories/" + username
			fetchContent(url, path, ignoreCache)
			with open(path, "r") as jsonContent:
				jsonDict = json.load(jsonContent)
				repositories = sorted([ x["href"] for repo in jsonDict["values"]
					for x in repo["links"]["clone"] if "http" in x["name"] ])
				starred = [] # not available on BitBucket

	except:
		print("Error:\n\n" + traceback.format_exc())
	os.makedirs(backupsDir, exist_ok=True)
	os.makedirs(backupsDir / username, exist_ok=True)
	os.makedirs(backupsDir / username / "repositories", exist_ok=True)
	if len(starred) != 0:
		os.makedirs(backupsDir / username / "starred", exist_ok=True)
	saveRepos(repositories, "repositories", username, onlyLastCommit=onlyLastCommit, ignoreCache=ignoreCache)
	saveRepos(starred, "starred", username, onlyLastCommit=onlyLastCommit, ignoreCache=ignoreCache)


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Please provide a repository to backup.")
		exit()
	saveStarred=isTrue(sys.argv[2]) if len(sys.argv) >= 3 else False
	onlyLastCommit=isTrue(sys.argv[3]) if len(sys.argv) >= 4 else False
	ignoreCache=isTrue(sys.argv[4]) if len(sys.argv) >= 5 else False
	backup(sys.argv[1], saveStarred=saveStarred, onlyLastCommit=onlyLastCommit, ignoreCache=ignoreCache)
