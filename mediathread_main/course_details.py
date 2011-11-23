UPLOAD_PERMISSION_KEY = "upload_permission"

UPLOAD_PERMISSION_ADMINISTRATOR = 0
UPLOAD_PERMISSION_INSTRUCTOR = 1
UPLOAD_PERMISSION_STUDENT = 2

UPLOAD_PERMISSION_LEVELS = [ (UPLOAD_PERMISSION_ADMINISTRATOR, 'Administrator'), 
                             (UPLOAD_PERMISSION_INSTRUCTOR, 'Instructor'), 
                             (UPLOAD_PERMISSION_STUDENT, 'Student')]

UPLOAD_PERMISSION_DEFAULT = UPLOAD_PERMISSION_INSTRUCTOR

def can_upload(user, course):
    value = int(course.get_detail(UPLOAD_PERMISSION_KEY, UPLOAD_PERMISSION_DEFAULT))
    if user.is_staff:
        return True
    elif course.is_faculty(user) and value >= UPLOAD_PERMISSION_INSTRUCTOR:
        return True
    elif value == UPLOAD_PERMISSION_STUDENT:
        return True 