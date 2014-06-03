# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Getting Things GNOME! - a personal organizer for the GNOME desktop
# Copyright (c) 2008-2013 - Lionel Dricot & Bertrand Rousseau
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

# Functions to convert a Task object to an XML string and back
import xml.dom.minidom as minidom
import xml.sax.saxutils as saxutils
from datetime import datetime

from GTG.tools import cleanxml
from GTG.tools.dates import Date


def get_text(node):
    if len(node.childNodes) > 0:
        return node.firstChild.nodeValue.strip()
    else:
        return ""


def read_node(xmlnode, name):
    node_list = xmlnode.getElementsByTagName(name)
    if len(node_list) > 0:
        return get_text(node_list[0])
    else:
        return ""

# Take an empty task, an XML node and return a Task.
def task_from_xml(task, xmlnode):
    # print "********************************"
    # print xmlnode.toprettyxml()

    task.set_uuid(xmlnode.getAttribute("uuid"))
    task.set_title(read_node(xmlnode, "title"))
    if xmlnode.getAttribute("recur") != "":
        task.set_recurrence_attribute(xmlnode.getAttribute("recur"))
        for node in xmlnode.childNodes:
            if node.tagName == "recurring":
                repeats = node.childNodes[0].tagName
                task.set_recurrence_repeats(repeats)
                frequency = read_node(xmlnode, "frequency")
                task.set_recurrence_frequency(frequency)
                if repeats == "Weekly":
                    days = read_node(xmlnode, "day")
                    task.set_recurrence_days(days)
                elif repeats == "Monthly":
                    onthe = read_node(xmlnode, "on")
                    onday = read_node(xmlnode, "day")
                    task.set_recurrence_onthe(onthe)
                    task.set_recurrence_onday(onday)
                endon_child = node.childNodes[1]
                for node in endon_child.childNodes:
                    task.set_recurrence_endson(
                        node.tagName, read_node(xmlnode, "%s"%(node.tagName)))

    status = xmlnode.getAttribute("status")
    donedate = Date.parse(read_node(xmlnode, "donedate"))
    task.set_status(status, donedate=donedate)

    duedate = Date(read_node(xmlnode, "duedate"))
    task.set_due_date(duedate)

    startdate = Date(read_node(xmlnode, "startdate"))
    task.set_start_date(startdate)

    modified = read_node(xmlnode, "modified")
    if modified != "":
        modified = datetime.strptime(modified, "%Y-%m-%dT%H:%M:%S")
        task.set_modified(modified)

    tags = xmlnode.getAttribute("tags").replace(' ', '')
    tags = (tag for tag in tags.split(',') if tag.strip() != "")
    for tag in tags:
        # FIXME why unescape????
        task.tag_added(saxutils.unescape(tag))

    # FIXME why we need to convert that through an XML?
    content = read_node(xmlnode, "content")
    if content != "":
        content = "<content>%s</content>" % content
        content = minidom.parseString(content).firstChild.toxml()
        task.set_text(content)

    for subtask in xmlnode.getElementsByTagName("subtask"):
        task.add_child(get_text(subtask))

    for attr in xmlnode.getElementsByTagName("attribute"):
        if len(attr.childNodes) > 0:
            value = get_text(attr)
        else:
            value = ""
        key = attr.getAttribute("key")
        namespace = attr.getAttribute("namespace")
        task.set_attribute(key, value, namespace=namespace)

    # FIXME do we need remote task ids? I don't think so
    # FIXME if so => rework them into a more usable structure!!!
    #                (like attributes)
    # REMOTE TASK IDS
    '''
    remote_ids_list = xmlnode.getElementsByTagName("task-remote-ids")
    for remote_id in remote_ids_list:
        if remote_id.childNodes:
            node = remote_id.childNodes[0]
            backend_id = node.firstChild.nodeValue
            remote_task_id = node.childNodes[1].firstChild.nodeValue
            task.add_remote_id(backend_id, remote_task_id)
            '''

    return task

# FIXME maybe pretty XML should be enough for this...
# Task as parameter the doc where to put the XML node


def task_to_xml(doc, task):
    t_xml = doc.createElement("task")
    whence = task.get_recurrence_repeats()
    recur_xml = doc.createElement("recurring")
    whence_xml = doc.createElement("%s"%(whence))
    repeats_xml = doc.createElement("repeats")
    endson_xml = doc.createElement("endson")
    t_xml.appendChild(recur_xml)
    recur_xml.appendChild(whence_xml)
    whence_xml.appendChild(repeats_xml)
    recur_xml.appendChild(endson_xml)
    t_xml.setAttribute("id", task.get_id())
    t_xml.setAttribute("status", task.get_status())
    t_xml.setAttribute("uuid", task.get_uuid())
    recure_val = task.get_recurrence_attribute()
    if recure_val == "True":
        t_xml.setAttribute("recur", task.get_recurrence_attribute())

    tags_str = ""
    for tag in task.get_tags_name():
        tags_str = tags_str + saxutils.escape(str(tag)) + ","
    t_xml.setAttribute("tags", tags_str[:-1])
    cleanxml.addTextNode(doc, t_xml, "title", task.get_title())
    cleanxml.addTextNode(doc, repeats_xml, "frequency", task.get_recurrence_frequency())
    if whence == "Weekly":
        cleanxml.addTextNode(doc, repeats_xml, "day", task.get_recurrence_days())
    elif whence == "Monthly":
        cleanxml.addTextNode(doc, repeats_xml, "on", task.get_recurrence_onthe())
        cleanxml.addTextNode(doc, repeats_xml, "day", task.get_recurrence_onday())
    if task.endson == "date":
        cleanxml.addTextNode(doc, endson_xml, "%s"%(task.endson), task.get_endon_date().xml_str())
    else:
        cleanxml.addTextNode(doc, endson_xml, "%s"%(task.endson), task.get_recurrence_endson())
    cleanxml.addTextNode(doc, t_xml, "duedate", task.get_due_date().xml_str())
    cleanxml.addTextNode(doc, t_xml, "modified", task.get_modified_string())
    cleanxml.addTextNode(doc, t_xml, "startdate",
                         task.get_start_date().xml_str())
    cleanxml.addTextNode(doc, t_xml, "donedate",
                         task.get_closed_date().xml_str())
    childs = task.get_children()
    for c in childs:
        cleanxml.addTextNode(doc, t_xml, "subtask", c)
    for a in task.attributes:
        namespace, key = a
        content = task.attributes[a]
        element = doc.createElement('attribute')
        element.setAttribute("namespace", namespace)
        element.setAttribute("key", key)
        element.appendChild(doc.createTextNode(content))
        t_xml.appendChild(element)
    tex = task.get_text()
    if tex:
        # We take the xml text and convert it to a string
        # but without the "<content />"
        element = minidom.parseString(tex)
        temp = element.firstChild.toxml().partition("<content>")[2]

        desc = temp.partition("</content>")[0]
        # t_xml.appendChild(element.firstChild)
        cleanxml.addTextNode(doc, t_xml, "content", desc)
    # self.__write_textnode(doc,t_xml,"content",t.get_text())

    # REMOTE TASK IDS
    remote_ids_element = doc.createElement("task-remote-ids")
    t_xml.appendChild(remote_ids_element)
    remote_ids_dict = task.get_remote_ids()
    for backend_id, task_id in remote_ids_dict.items():
        backend_element = doc.createElement('backend')
        remote_ids_element.appendChild(backend_element)
        backend_element.appendChild(doc.createTextNode(backend_id))
        task_element = doc.createElement('task-id')
        backend_element.appendChild(task_element)
        task_element.appendChild(doc.createTextNode(task_id))

    return t_xml
