#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#

from string import Template
import os
import urllib2

class Menuentry(object):
    def __init__(self,menuentry,path,vmlinuz, options, initrd, chroot="/home/pxe/tftp/grub"):
        self.menuentry = menuentry
        self.path = path
        self.vmlinuz = vmlinuz
        self.options = options
        self.initrd = initrd
        self.chroot = chroot
        if menuentry is None or vmlinuz is None or initrd is None:
            raise
        if options is None:
            self.options=""

    def __str__(self):
        tempT = """
        menuentry "$menuentry" {
            linux $vmlinuz $options
            initrd $initrd
        }
        """

        tempTemplate = Template(tempT)
        return tempTemplate.safe_substitute(menuentry=self.menuentry, vmlinuz=os.path.join(self.path,self.vmlinuz), options=self.options, initrd=os.path.join(self.path,self.initrd))


class deepin_dailylive_next_menuentry(Menuentry):
    def __init__(self):
        self.menuentry="Deepin Dailylive Next"
        self.path="/live-boot/deepin-next/caser"
        self.vmlinuz="vmlinuz"
        self.options="boot=casper netboot=nfs nfsroot=10.0.0.6:/nfsroot/deepin-next/desktop/current/amd64/ quiet splash locale=zh_CN"
        self.initrd="initrd.lz"
        super(deepin_dailylive_next_menuentry,self).__init__(self.menuentry, self.path,self.vmlinuz, self.options, self.initrd)
        self.valicate()

    def _get_timestamp(self, url):
        import re
        import time
        try:
            page = urllib2.urlopen(url)
        except:
            return None
        if page.getcode() != 200:
            return None
        timestr=None
        for i in page.readlines():
            m = re.match(r"<a.*>vmlinuz.*</a>\s+(.*\s\S*)\s+.+", i)
            if m:
                timestr=m.group(1).strip()
                break
        if timestr is None:
            return None
        timestruct=time.strptime(timestr, "%d-%b-%Y %H:%M")
        timestamp=time.strftime("(%Y%m%d %H:%M)",timestruct)
        return timestamp

    def download(self, url, savepath):
        try:
            r=urllib2.urlopen(url)
            f=open(savepath,'wb')
            f.write(r.read())
            f.close()
        except:
            raise

    def valicate(self, url="http://cdimage/nfsroot/deepin-next/desktop/current/amd64/casper"):
        timestamp=self._get_timestamp(url)
        if not timestamp:
            return False

        _real_root_path = os.path.join(self.chroot, self.path.lstrip('/'))
        if not os.path.exists(_real_root_path):
            print "Make dirs %s" % _real_root_path
            os.makedirs(_real_root_path)

        if os.path.exists(os.path.join(_real_root_path, self.vmlinuz)):
            os.unlink(os.path.join(_real_root_path,self.vmlinuz))
        if os.path.exists(os.path.join(_real_root_path, self.initrd)):
            os.unlink(os.path.join(_real_root_path,self.initrd))

        try:
            self.download(url+'/vmlinuz', os.path.join(_real_root_path, self.vmlinuz))
            self.download(url+'/initrd.lz', os.path.join(_real_root_path, self.initrd))
        except:
            return False

        self.menuentry+=" %s" % timestamp

    def __str__(self):
        tempT = """
        menuentry "$menuentry" {
            linux $vmlinuz $options
            initrd $initrd
        }
        menuentry "LiveInstaller $menuentry" {
            linux $vmlinuz $options livecd-installer
            initrd $initrd
        }
        """

        tempTemplate = Template(tempT)
        return tempTemplate.safe_substitute(menuentry=self.menuentry, vmlinuz=os.path.join(self.path,self.vmlinuz), options=self.options, initrd=os.path.join(self.path,self.initrd))

class Submenu():
    def __init__(self,name):
        self.name = name
        self.menuentry = []

    def get_menuentry(self):
        return self.menuentry

    def append(self,menuentry):
        self.menuentry.append(menuentry)

    def __str__(self):
        strings = 'submenu "%s" {' % self.name
        for menuentry in self.get_menuentry():
            strings+=str(menuentry)
        strings+="}"
        return strings

class GrubCfg():
    def __init__(self):
        self.entry = []

    def get_entry(self):
        return self.entry

    def append(self,entry):
        self.entry.append(entry)

    def __str__(self):
        strings=""
        for entry in self.get_entry():
            strings+=str(entry)
        return strings

grubcfg=GrubCfg()

menus=Submenu('Deepin live Next')
daily_live_next=deepin_dailylive_next_menuentry()
menus.append(daily_live_next)

grubcfg.append(menus)
print grubcfg
