export enum JobUsage {
    Robotics,
    School,
    Home,
    Other,
}

export interface User {
    displayName: string;
    email: string;
    photoUrl?: string;
}

export interface Job {
    id: number;
    date: Date;
    name: string;
    owner: User;
    usage: JobUsage;
    origUrl?: string;
    stlUrl: string;
    thumbUrl?: string;
}
