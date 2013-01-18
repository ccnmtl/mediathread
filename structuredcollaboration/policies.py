class CollaborationPoliciesSingleton:
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


class CollaborationPolicy:
    """
    Base Collaboration Policy
    """
    def permission_to(self, collaboration, permission, request):
        rv = getattr(self, permission, lambda c, r: False)(collaboration,
                                                           request)
        return rv


class BasePublicPolicy:
    def read(self, collaboration, request):
        return True


class BaseProtectedPolicy:
    def read(self, collaboration, request):
        return request.user.is_authenticated()


class PolicyByType(CollaborationPolicy):
    """
    A common pattern is to have different policies for each class
    >>> PolicyByType(default=EditorsAreOwners,
    {Group:ParentEditorsAreOwners,} )
    """
    types = None
    default = None

    def __init__(self, default=None, policy_dict=None):
        assert(default is not None)
        self.types = policy_dict or dict()  # empty
        self.default = default

    def permission_to(self, collaboration, permission, request):
        col_type = getattr(collaboration.content_object, '__class__', None)
        return self.types.get(col_type,
                              self.default).permission_to(collaboration,
                                                          permission,
                                                          request)


class PublicEditorsAreOwners(CollaborationPolicy, BasePublicPolicy):
    """
    Implements a basic policy of people who can edit can also manage the group
    """

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


class ProtectedEditorsAreOwners(PublicEditorsAreOwners, BaseProtectedPolicy):
    """
    Implements a basic policy of people who can edit can also manage the group
    """
    pass


class PublicParentEditorsAreOwners(PublicEditorsAreOwners, BasePublicPolicy):
    """
    parent of the instance's editors are the current's owners
    """

    def manage(self, collaboration, request):
        return collaboration.get_parent().permission_to('edit', request)


class ProtectedParentEditorsAreOwners(PublicParentEditorsAreOwners,
                                      BaseProtectedPolicy):
    pass


class PrivateEditorsAreOwners(PublicEditorsAreOwners):
    def read(self, collaboration, request):
        return (request.user.is_staff or self.edit(collaboration, request))


CollaborationPolicies.register_policy(CollaborationPolicy,
                                      'forbidden',
                                      'Forbidden to everyone')
CollaborationPolicies.register_policy(PublicEditorsAreOwners,
                                      'PublicEditorsAreOwners',
                                      'Editors can manage the group, \
                                       Content is world-readable')
CollaborationPolicies.register_policy(ProtectedEditorsAreOwners,
                                      'ProtectedEditorsAreOwners',
                                      'Editors can manage the group, \
                                      Viewing requires authentication')
CollaborationPolicies.register_policy(PublicParentEditorsAreOwners,
                                      'PublicParentEditorsAreOwners',
                                      'Parent editors can manage the group, \
                                      Content is world-readable')
CollaborationPolicies.register_policy(ProtectedParentEditorsAreOwners,
                                      'ProtectedParentEditorsAreOwners',
                                      'Parent editors can manage the group, \
                                      Viewing requires authentication')

CollaborationPolicies.register_policy(PrivateEditorsAreOwners,
                                      'PrivateEditorsAreOwners',
                                      'User and group can view/edit/manage. \
                                      Staff can read')
