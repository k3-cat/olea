def init(self):
    for char in set(CONVERT.values()):
        data = self.graph.post(req='/me/drive/root/children',
                               data={
                                   "name": char,
                                   "folder": {},
                                   "@microsoft.graph.conflictBehavior": "rename"
                               })
    return True


# and then move those folders into a new folder 'olea-storage',
# which located under the root
