/*
 * tak pisałem C++ w 2004 roku :D
 */
int mutex::lock()
{
    switch (_kind)
    {
    case FAST:
        if (_count == 0)
        {
            pthread_mutex_lock(&_lock);
            _owner = pthread_self();
            _count = 1;
        } else
            return EPERM;
        break;

    case ERRORCHECKING:
        if (pthread_equal(_owner, pthread_self()))
            return EDEADLK;
        else
        {
            pthread_mutex_lock(&_lock);
            _count = 1;
            _owner = pthread_self();
        };
        break;

    case RECURSIVE:
        if (pthread_equal(_owner, pthread_self()))
            _count++;
        else
        {
            pthread_mutex_lock(&_lock);
            _count = 1;
            _owner = pthread_self();
        };
        break;
    };
    return 1;
};
