"""
A read only StorageInterface that look at an email server.
"""

import logging
import time

from imaplib import IMAP4_SSL
from email import message_from_string
from email.utils import parseaddr, parsedate

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError, NoUserError
from tiddlyweb.stores import StorageInterface

class Store(StorageInterface):


    def __init__(self, environ=None):
        super(Store, self).__init__(environ)
        server_info = self.environ['tiddlyweb.config']['server_store'][1]
        self.server = server_info['imap_server']
        self.user = server_info['user']
        self.password = server_info['password']
        self.prefix = server_info['prefix']
        self.imap = self._login()

    def _login(self):
        imap = IMAP4_SSL(self.server)
        imap.login(self.user, self.password)
        return imap

    def bag_get(self, bag):
        logging.debug('getting bag: %s' % bag.name)
        try:
            count = self.imap.select('%s/%s' % (self.prefix, bag.name))
        except readonly:
            pass
        if count[0] == 'NO':
            return bag
        if hasattr(bag, 'notiddlers') and bag.notiddlers:
            return bag

        typ, data = self.imap.search(None, 'ALL')
        for num in data[0].split():
            typ, data = self.imap.fetch(num, '(RFC822)')
            message = message_from_string(data[0][1])
            if not message.is_multipart():
                bag.add_tiddler(Tiddler('%s:%s' % (message['message-id'], message['subject'])))
        return bag

    def tiddler_get(self, tiddler):
        count = self.imap.select('%s/%s' % (self.prefix, tiddler.bag), True)
        logging.debug('tiddler get count: %s:%s' % (count[0], count[1]))
        message_id = tiddler.title.split(':', 1)[0]
        typ, data = self.imap.search(None, '(HEADER Message-ID "%s")' % message_id)
        typ, data = self.imap.fetch(data[0], '(RFC822)')
        message = message_from_string(data[0][1])
        tiddler.text = message.get_payload()
        tiddler.modifier = parseaddr(message['from'])[1]
        date = message['date']
        parsed_date = parsedate(date)
        tiddler.modified = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.mktime(parsed_date)))
        return tiddler

    def list_bags(self):
        typ, mailboxes = self.imap.list('', '%s/a%%' % self.prefix)
        bags = []
        for mailbox in mailboxes:
            name = mailbox.split('%s/' % self.prefix)[1]
            if name:
                bags.append(Bag(name))
        return bags


def exercise(hostname, user, password):
    imap = IMAP4_SSL(hostname)
    imap.login(user, password)
    imap.select()
    typ, data = imap.search(None, 'ALL')
    messages = []
    for num in data[0].split():
        typ, data = imap.fetch(num, '(RFC822)')
        message = message_from_string(data[0][1])
        if not message.is_multipart():
            messages.append(message)

    for message in messages:
        print 'Subject:\t%s' % message['subject']
        print 'From:\t%s' % message['from']
        print 'Date:\t%s' % message['date']
        print 'ID:\t%s' % message['message-id']
        print
        print message.get_payload()
        id = message['message-id']

    typ, data = imap.search(None, '(HEADER Message-ID "%s")' % id)
    typ, data = imap.fetch(data[0], '(RFC822)')
    print data[0][1]




if __name__ == '__main__':
    exercise('example.com', 'boom','xxxxx')
