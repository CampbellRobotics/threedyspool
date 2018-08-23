import { Component, OnInit } from '@angular/core';
import { animate, state, style, transition, trigger } from '@angular/animations';
import { JOBS } from '../mock-jobs';
import { Job, JobUsage } from '../job';
import { JobService } from '../services/job.service';

/**
 * @title Jobs list with expandable rows
 */
@Component({
    selector: 'app-jobs-list',
    styleUrls: ['jobs-list.component.css'],
    templateUrl: 'jobs-list.component.html',
    animations: [
        trigger('detailExpand', [
            state('collapsed', style({ height: '0px', minHeight: '0', display: 'none' })),
            state('expanded', style({ height: '*' })),
            transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)')),
        ]),
    ],
})
export class JobsListComponent implements OnInit {
    dataSource = JOBS;
    columnsToDisplay = ['name', 'date', 'owner', 'usage'];
    expandedJob?: Job;
    jobs: Job[] = [];

    getJobType(val: keyof typeof JobUsage) {
        return JobUsage[val];
    }

    constructor(private jobService: JobService) { }

    getJobs(): void {
        this.jobService.getJobs().subscribe(jobs => this.jobs = jobs);
    }

    ngOnInit() {
        this.getJobs();
    }
}
