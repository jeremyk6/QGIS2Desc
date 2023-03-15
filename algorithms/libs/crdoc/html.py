from .doc import *

class HTMLNode(Node):

	def __init__(self, tag):
		super().__init__(tag)
	
	def toString(self, depth=0):
		indent = ""
		for i in range(depth): indent += "    "
		doc = "%s<%s>"%(indent, self.tag)
		for child in self.children:
			doc += "\n%s"%(child.toString(depth=depth+1))
		doc += "\n%s</%s>"%(indent, self.tag)
		return(doc)

class DocumentRoot(HTMLNode):

	def __init__(self, title):
		super().__init__("html")
		super().add_child(
			HTMLNode("head").add_child(
				HTMLNode("title").add_child(
					Text(title)
				)
			)
		)
		super().add_child(
			HTMLNode("body")
		)

	def add_child(self, node):
		self.children[-1].add_child(node)
		return(self)

class Paragraph(HTMLNode):

	def __init__(self):
		super().__init__("p")

class List(HTMLNode):

	def __init__(self):
		super().__init__("ul")

class NumberedList(HTMLNode):

	def __init__(self):
		super().__init__("ol")

class ListElement(HTMLNode):

	def __init__(self):
		super().__init__("li")

class Title1(HTMLNode):

	def __init__(self):
		super().__init__("h1")

class Title2(HTMLNode):

	def __init__(self):
		super().__init__("h2")

class Title3(HTMLNode):

	def __init__(self):
		super().__init__("h3")

class Text(HTMLNode):

	def __init__(self, value):
		super().__init__("")
		self.value = value

	def toString(self, depth=0):
		indent = ""
		for i in range(depth): indent += "    "
		doc = "%s%s"%(indent, self.value)
		return(doc)

