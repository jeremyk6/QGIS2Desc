class Node:

	def __init__(self, tag):
		self.tag = tag
		self.children = []
	
	def add_child(self,node):
		self.children.append(node)
		return(self)
	
	def toString(self, depth=0):
		tab = ""
		for i in range(depth): tab += "    "
		doc = "%s%s"%(tab, self.tag)
		for child in self.children:
			doc += "\n%s"%(child.toString(depth=depth+1))
		doc += "\n%s/%s"%(tab,self.tag)
		return(doc)
