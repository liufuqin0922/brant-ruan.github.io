#!/usr/bin/env python

# This script is used to extract data wanted from LvMeng-Scanner
# by brant-ruan
# 2018-04-10 version 1.0

from bs4 import BeautifulSoup
import time

# Global Configurations
# You may need change them if it is not the same with yours
URL = "index.html"
VULN_TABLE_ID = "vuln_distribution"
VULN_HIGH = "vuln_high"
VULN_MIDDLE = "vuln_middle"
SCANNER_NAME = "绿盟"
# Result lists
VHList = []
VMList = []

class Vul:
	'''
	One vulnerability's detail
	'''
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
	def Show(self):
		print(self.name)
		print(self.hosts)
		print(self.cve)

def VulnAppend(VList, VSet):
	
	for vuln in VSet:
		v = Vul()
		v.setName(vuln.span.get_text())
		vulnDtl = vuln.next_sibling.next_sibling.find_all(name = "tr")
		v.setHosts(vulnDtl[0].td.get_text().replace("&nbsp", ""))
		v.setText(vulnDtl[1].td.get_text().replace("&nbsp", ""))
		v.setRank(vulnDtl[3].td.get_text().replace("&nbsp", ""))
		if len(vulnDtl) >= 7 and vulnDtl[6].th.get_text() == 'CVE编号':
			v.setCVE(vulnDtl[6].td.get_text().replace("&nbsp", ""))
		else:
			v.setCVE('无或未知')
		VList.append(v)

def Init():

	htmlfile = open(URL, 'r')
	htmlpage = htmlfile.read()
	# if you have lxml, it is more quick
	soup = BeautifulSoup(htmlpage, "lxml")
	#soup = BeautifulSoup(htmlpage, "html.parser")
	htmlfile.close()

	vulnTable = soup.find(id = VULN_TABLE_ID)
	vulnHighSet = vulnTable.find_all(name = "tr", attrs = {"class": VULN_HIGH})
	vulnMiddleSet = vulnTable.find_all(name = "tr", attrs = {"class": VULN_MIDDLE})

	VulnAppend(VHList, vulnHighSet)
	VulnAppend(VMList, vulnMiddleSet)

def Prompt():
	print("Ensure that:")
	print("\t 1. Beautiful Soup installed")
	print("If not, you can use `apt-get install Python-bs4` on Debian or Ubuntu to install it.")
	print("You can also try `pip install beautifulsoup4` or `easy_install beautifulsoup4` if `apt-get` not available.")
	print("\t 2. lxml parser installed")
	print("If not, you can use `apt-get install Python-lxml` on Debian or Ubuntu to install it.")
	print("You can also try `pip install lxml` or `easy_install lxml` if `apt-get` not available.")
	print("You can also use another parser. If you choose other parsers, you should configure it in the code before you run it.")
	print("\t 3. This tool has been put under the same directory of `index.html`, which you want to analyse")
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
		content = content + "### 目标主机" + "\n\n" + res.getHosts() + "\n\n"
		if opt == 'y' or opt =='Y':
			content = content + "### 详细内容" + "\n\n" + res.getText() + "\n\n"
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
	validOpt = "123456q"
	while True:
		result = []
		print()
		print("【" + SCANNER_NAME + "扫描器结果导出】")		
		print("[1] 导出所有[高危]漏洞 (rank: 7 <= x <= 10)")
		print("[2] 导出所有[中危]漏洞 (rank: 4 <= x < 7)")
		print("[3] 导出所有[高危]/[中危]漏洞 (rank: 4 <= x <= 10)")
		print("[4] 按照关键词，导出所有[高危]漏洞")
		print("[5] 按照关键词，导出所有[中危]漏洞")
		print("[6] 按照关键词，导出所有[高危]/[中危]漏洞")
		print("[q] 退出")
		print()

		you = input("$ ")
		if you not in validOpt:
			print("invalid option.")
			continue
		if you == 'q':
			return 0

		if you == '1':
			result = VHList
		if you == '2':
			result = VMList
		if you == '3':
			result = VHList + VMList

		keyword_flag = 0
		workList = []
		if you == '4':
			workList = VHList
			keyword_flag = 1
		if you == '5':
			workList = VMList
			keyword_flag = 1
		if you == '6':
			workList = VHList + VMList
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
