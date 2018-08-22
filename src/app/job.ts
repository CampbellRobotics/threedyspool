export enum JobUsage {
    Robotics,
    School,
    Home,
    Other,
}

export class User {
    displayName: string;
    email: string;
    photoUrl?: string;
}

export class Job {
    id: number;
    date: Date;
    name: string;
    owner: User;
    usage: JobUsage;
}
