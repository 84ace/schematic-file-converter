#!/usr/bin/env python
""" The Eagle Format Parser """

from core.design import Design
from xml.etree.ElementTree import ElementTree


class Eagle:
    """ The Eagle Format Parser """

    def __init__(self):
        pass


    def parse(self, filename):
        """ Parse an Eagle file into a design """
        #design = design()
        #import an xmltree from the file provided
       	xmltree = ElementTree(file=filename)
        xmlroot = xmltree.getroot()
		
        return xmltree

