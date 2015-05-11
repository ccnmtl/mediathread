from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.factories import CollaborationFactory, UserFactory
from structuredcollaboration.policies import PublicEditorsAreOwners, \
    PrivateEditorsAreOwners, CollaborationPolicies, CollaborationPolicy


class PoliciesTest(TestCase):

    def test_forbidden(self):
        policy = CollaborationPolicies.registered_policies['forbidden']
        collaboration = CollaborationFactory()
        request = RequestFactory()

        request.user = collaboration.user
        self.assertFalse(policy.permission_to(collaboration, 'read', request))
        self.assertFalse(policy.permission_to(collaboration, 'edit', request))
        self.assertFalse(policy.permission_to(
            collaboration, 'manage', request))
        self.assertFalse(policy.permission_to(
            collaboration, 'delete', request))

    def test_register(self):
        CollaborationPolicies.register_policy(CollaborationPolicy,
                                              'custom', 'description')
        self.assertTrue('custom' in CollaborationPolicies.registered_policies)

    def test_public_editors_are_owners(self):
        policy = PublicEditorsAreOwners()
        collaboration = CollaborationFactory()
        request = RequestFactory()

        request.user = collaboration.user
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

        request.user = UserFactory()  # random user
        self.assertTrue(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))

        collaboration.group.user_set.add(request.user)  # now a group member
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

    def test_private_editors_are_owners(self):
        policy = PrivateEditorsAreOwners()
        collaboration = CollaborationFactory()
        request = RequestFactory()

        request.user = collaboration.user
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

        request.user = UserFactory()  # random user
        self.assertFalse(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))

        collaboration.group.user_set.add(request.user)  # now a group member
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

        request.user = UserFactory(is_staff=True)
        self.assertTrue(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))
