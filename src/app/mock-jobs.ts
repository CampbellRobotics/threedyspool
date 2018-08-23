import { Job, User, JobUsage } from './job';

const johnDoe: User = { displayName: 'John Doe', email: 'john@example.com' };
const janeDoe: User = { displayName: 'Jane Doe', email: 'jane@example.com' };

export const JOBS: Job[] = [
    {
        name: 'Jobby job with a long name',
        id: 1,
        date: new Date('2018-08-20T02:00'),
        stlUrl: 'https://example.com/test1.stl',
        origUrl: 'https://example.com/orig1.stp',
        thumbUrl: 'assets/test-stanford-bunny.jpg',
        owner: johnDoe,
        usage: JobUsage.Home
    },
    {
        name: 'Robot stop switch',
        id: 2,
        date: new Date('2016-01-01T01:00'),
        stlUrl: 'https://example.com/test2.stl',
        owner: janeDoe,
        usage: JobUsage.Robotics
    },
];
