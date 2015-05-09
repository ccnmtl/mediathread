class CollaborationPolicy(object):
    """
    Base Collaboration Policy
    """
    def permission_to(self, collaboration, permission, request):
        rv = getattr(self, permission, lambda c, r: False)(collaboration,
                                                           request)
        return rv


class PublicEditorsAreOwners(CollaborationPolicy):
    """
    Implements a basic policy of people who can edit can also manage the group
    """
    def read(self, collaboration, request):
        return True

    def edit(self, collaboration, request):
        user = request.user
        if user.is_authenticated():
            if user == collaboration.user:
                return True
            if collaboration.group_id:
                qs = collaboration.group.user_set.filter(pk=user.pk)
                return len(qs) > 0
        return False

    manage = edit
    delete = edit


class PrivateEditorsAreOwners(PublicEditorsAreOwners):
    def read(self, collaboration, request):
        return (request.user.is_staff or self.edit(collaboration, request))


class CollaborationPoliciesSingleton(object):
    # purposely setting it where it stays static on the instance
    registered_policies = dict()
    policy_options = dict()

    def register_policy(self, policy_class, policy_key, policy_title):
        assert(len(policy_key) < 512)
        self.registered_policies[policy_key] = policy_class()
        self.policy_options[policy_key] = policy_title

    def __iter__(self):
        return iter(self.policy_options.items())

CollaborationPolicies = CollaborationPoliciesSingleton()


CollaborationPolicies.register_policy(CollaborationPolicy,
                                      'forbidden',
                                      'Forbidden to everyone')
CollaborationPolicies.register_policy(PublicEditorsAreOwners,
                                      'PublicEditorsAreOwners',
                                      'Editors can manage the group, \
                                       Content is world-readable')
CollaborationPolicies.register_policy(PrivateEditorsAreOwners,
                                      'PrivateEditorsAreOwners',
                                      'User and group can view/edit/manage. \
                                      Staff can read')
