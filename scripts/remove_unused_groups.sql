/* 
For a while we have been creating groups from _every_ affiliation that djangowind passes us. Many of these are unused, and we now have > 35k groups, bogging down the admin screen

This sql query deletes rows  from auth_user_groups and then from auth_group for any group that is not currently affiated with a course

*/

DELETE FROM auth_user_groups WHERE group_id in (SELECT id FROM auth_group WHERE id NOT IN (SELECT group_id FROM courseaffils_course) AND id NOT IN (SELECT faculty_group_id FROM courseaffils_course) AND id NOT IN (SELECT group_id from structuredcollaboration_collaboration WHERE group_id IS NOT NULL));

DELETE FROM auth_group_permissions WHERE group_id in (SELECT id FROM auth_group WHERE id NOT IN (SELECT group_id FROM courseaffils_course) AND id NOT IN (SELECT faculty_group_id FROM courseaffils_course) AND id NOT IN (SELECT group_id from structuredcollaboration_collaboration WHERE group_id IS NOT NULL));

DELETE FROM auth_group WHERE id in (SELECT id FROM auth_group WHERE id NOT IN (SELECT group_id FROM courseaffils_course) AND id NOT IN (SELECT faculty_group_id FROM courseaffils_course) AND id NOT IN (SELECT group_id from structuredcollaboration_collaboration WHERE group_id IS NOT NULL));