import { Injectable } from '@angular/core';
import { JOBS } from '../mock-jobs';
import { Job } from '../job';
import { of, Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class JobService {

    constructor() { }
    getJobs(): Observable<Job[]> {
        return of(JOBS);
    }
}
