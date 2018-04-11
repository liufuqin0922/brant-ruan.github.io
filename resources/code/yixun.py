#!/usr/bin/env python

# This script is used to extract data wanted from YiXun-Scanner
# by brant-ruan
# 2018-04-11 version 1.0

from bs4 import BeautifulSoup
import time

# Global Configurations
# You may need change them if it is not the same with yours
SCANNER_NAME = "铱迅"
URL = "report.html"

VULN_EMER_CLASS = "y-report-ui-text-level-critical-b" # emergency
VULN_HIGH_CLASS = "y-report-ui-text-level-high-b"
VULN_MIDDLE_CLASS = "y-report-ui-text-level-medium-b"
# Result lists
VEList = []
VHList = []
VMList = []

class Vul:
	'''
	One vulnerability's detail
	'''
	def __init__(self):
		self.webdtl = ""
	def getName(self):
		return self.name
	def setName(self, name):
		self.name = name
	def getText(self):
		return self.text
	def setText(self, text):
		self.text = text
	def getHosts(self):
		return self.hosts
	def setHosts(self, hosts):
		self.hosts = hosts
	def getRank(self):
		return self.rank
	def setRank(self, rank):
		self.rank = rank
	def getCVE(self):
		return self.cve
	def setCVE(self, cve):
		self.cve = cve
	# for web details
	def getWebDtl(self):
		return self.webdtl
	def setWebDtl(self, webdtl):
		self.webdtl = webdtl
	def Show(self):
		print(self.name)
		print(self.hosts)
		print(self.cve)

def HostVulnAppend(VList, VSet):

	VULN_HOST_DETAIL_CLASS = "y-report-ui-object-tab-panel-content-frame"
	VULN_HOST_IP_CLASS = "y-report-ui-object-accordion-list-item-header"

	for vuln in VSet:
		# remove noise
		if vuln.parent.name == 'p':
			continue
		v = Vul()
		# find rank
		v.setRank(vuln.get_text())
		# find name
		v.setName(vuln.parent.get_text())
		vulnDtl = vuln.parent.parent.next_sibling.find(name="div", attrs={'class': VULN_HOST_DETAIL_CLASS})
		vulnDtlList = vulnDtl.find_all(name = "div", recursive = False)
		# find host-list
		ips = vulnDtlList[0].find_all(name="div", attrs={'class': VULN_HOST_IP_CLASS})
		ip_str = ""
		for ip in ips:
			ip_str = ip_str + ip.get_text() + ", "
		v.setHosts(ip_str)
		# find text
		v.setText(vulnDtlList[1].get_text())
		# find cve
		cve_url = vulnDtlList[3].tbody.tr.find_all(name="a")
		cve_str = ""
		for cve in cve_url:
			cve_str = cve_str + cve.get_text() + ", "
		v.setCVE(cve_str)
		VList.append(v)

def HostVulnHandle(soup):

	VULN_HOST_ID = "y-section-index-root-4-3"

	vulnTable = soup.find(id = VULN_HOST_ID)
	vulnEmerSet = vulnTable.find_all(name="span", attrs={'class': VULN_EMER_CLASS})
	vulnHighSet = vulnTable.find_all(name="span", attrs={'class': VULN_HIGH_CLASS})
	vulnMiddleSet = vulnTable.find_all(name="span", attrs={'class': VULN_MIDDLE_CLASS})

	HostVulnAppend(VEList, vulnEmerSet)
	HostVulnAppend(VHList, vulnHighSet)
	HostVulnAppend(VMList, vulnMiddleSet)

def WebVulnAppend(VList, VSet):

	VULN_WEB_DETAIL_CLASS = "y-report-ui-object-tab-panel-content-frame"
	VULN_WEB_DETAIL_CHILD_CLASS = "y-report-ui-object-tab-panel-content-element"
	VULN_WEB_DOMAIN_CLASS = "y-report-ui-object-accordion-list-item-header"

	for vuln in VSet:
		# remove noise
		if vuln.parent.name == 'p':
			continue
		v = Vul()
		# find rank
		v.setRank(vuln.get_text())
		# find name
		v.setName(vuln.parent.get_text())
		vulnDtl = vuln.parent.parent.next_sibling.find(name="div", attrs={'class': VULN_WEB_DETAIL_CLASS})
		vulnDtlChild = vulnDtl.div
		# find domains and text
		domains = vulnDtlChild.find_all(name="div", attrs={'class': VULN_WEB_DOMAIN_CLASS})
		domains_str = ""
		text = ""
		for domain in domains:
			domains_str = domains_str + domain.get_text() + "\n"
			detail = domain.next_sibling
			detailList = detail.tbody.find_all(name="tr", recursive=False)
			text = text + domain.get_text() + "\n" + detailList[2].get_text() + '\n' + \
				detailList[3].get_text() + '\n' + detailList[4].get_text() + "\n\n"
		v.setHosts(domains_str)
		v.setWebDtl(text)
		# find cve
		v.setCVE("无或未知")
		VList.append(v)

def WebVulnHandle(soup):
	
	VULN_WEB_ID = "y-section-index-root-5-3"

	vulnTable = soup.find(id = VULN_WEB_ID)
	vulnEmerSet = vulnTable.find_all(name="span", attrs={'class': VULN_EMER_CLASS})
	vulnHighSet = vulnTable.find_all(name="span", attrs={'class': VULN_HIGH_CLASS})
	vulnMiddleSet = vulnTable.find_all(name="span", attrs={'class': VULN_MIDDLE_CLASS})

	WebVulnAppend(VEList, vulnEmerSet)
	WebVulnAppend(VHList, vulnHighSet)
	WebVulnAppend(VMList, vulnMiddleSet)


def Init():
	htmlfile = open(URL, 'r')
	htmlpage = htmlfile.read()
	# if you have lxml, it is more quick
	soup = BeautifulSoup(htmlpage, "lxml")
	#soup = BeautifulSoup(htmlpage, "html.parser")
	htmlfile.close()

	HostVulnHandle(soup)
	WebVulnHandle(soup)

def Prompt():
	print("Ensure that:")
	print("\t 1. Beautiful Soup installed")
	print("If not, you can use `apt-get install Python-bs4` on Debian or Ubuntu to install it.")
	print("You can also try `pip install beautifulsoup4` or `easy_install beautifulsoup4` if `apt-get` not available.")
	print("\t 2. lxml parser installed")
	print("If not, you can use `apt-get install Python-lxml` on Debian or Ubuntu to install it.")
	print("You can also try `pip install lxml` or `easy_install lxml` if `apt-get` not available.")
	print("You can also use another parser. If you choose other parsers, you should configure it in the code before you run it.")
	print("\t 3. This tool has been put under the same directory of `report.html`, which you want to analyse")
	print()
	print("For more details, refer to official document.")
	print("It may be `https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh` :)")
	print()

def Export(result):
	filename = input("input filename: ")
	opt = input("with details or not? (y/n): ")
	content = "[toc] \n\n" + "# " + SCANNER_NAME + "扫描器处理结果" + "\n\n" + "时间: " + time.asctime() + "\n\n"
	i = 0
	for res in result:
		content = content + "## " + res.getName() + "\n\n"
		content = content + "### CVE编号" + "\n\n" + res.getCVE() + "\n\n"
		if res.getWebDtl() == "":
			content = content + "### 目标主机" + "\n\n" + res.getHosts() + "\n\n"
			if opt == 'y' or opt =='Y':
				content = content + "### 详细内容" + "\n\n" + res.getText() + "\n\n"
		if res.getWebDtl() != "":
			content = content + "### Web漏洞详细信息" + "\n\n" + res.getWebDtl() + "\n\n"
		i = i + 1
	f = open(filename, "w")
	f.write(content)
	print(str(i) + " vulns exported.")
	f.close()

def Match(vuln, keywords, keywordsN):
	flag1 = 0
	flag2 = 0
	for word in keywords:
		if word in vuln.getName():
			flag1 = 1
			break
	for wordN in keywordsN:
		if wordN not in vuln.getName():
			flag2 = 1
			break
	if keywords == []:
		flag1 = 1
	if keywordsN == []:
		flag2 = 1
	
	if flag1 == 1 and flag2 == 1:
		return True
	return False
	

def Operation():
	validOpt = "1234q"
	while True:
		result = []
		print()
		print("【" + SCANNER_NAME + "扫描器结果导出】")
		print("[1] 导出所有[紧急]/[高风险]漏洞")
		print("[2] 导出所有[紧急]/[高风险]/[中风险]漏洞")
		print("[3] 按照关键词，导出所有[紧急]/[高风险]漏洞")
		print("[4] 按照关键词，导出所有[紧急]/[高风险]/[中风险]漏洞")
		print("[q] 退出")
		print()

		you = input("$ ")
		if you not in validOpt:
			print("invalid option.")
			continue
		if you == 'q':
			return 0

		if you == '1':
			result = VEList + VHList
		if you == '2':
			result = VEList + VHList + VMList

		keyword_flag = 0
		workList = []
		if you == '3':
			workList = VEList + VHList
			keyword_flag = 1
		if you == '4':
			workList = VEList + VHList + VMList
			keyword_flag = 1
		
		back_flag = 0
		if keyword_flag == 1:
			keywords = []
			# inverse selection
			keywordsN = []
			while True:
				print("输入一个包含关键词, s 停止输入, b 返回")
				word = input("> ")
				if word == 's':
					break
				if word == 'b':
					back_flag = 1
					break
				keywords.append(word)
			if back_flag == 1:
				continue
			while True:
				print("输入一个不包含关键词, s 停止输入, b 返回")
				word = input("> ")
				if word == 's':
					break
				if word == 'b':
					back_flag = 1
					break
				keywordsN.append(word)
			for vuln in workList:
				if Match(vuln, keywords, keywordsN) == True:
					result.append(vuln)
		if back_flag == 1:
			continue

		Export(result)
				
def main():

	Prompt()

	w = input("Press Enter to continue, q to quit: ")
	if w == 'q':
		return 0
	
	print("Wait a moment...")
	Init()

	Operation()

if __name__ == "__main__":
	main()
