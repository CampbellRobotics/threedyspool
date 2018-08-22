import { Component, OnInit } from '@angular/core';
import { JOBS } from '../mock-jobs';
import { Job } from '../job';
import { trigger, state, style, animate, transition } from '@angular/animations';

@Component({
    selector: 'app-jobs-list',
    templateUrl: './jobs-list.component.html',
    styleUrls: ['./jobs-list.component.css'],
    animations: [
        trigger('detailExpand', [
            state('collapsed', style({height: '0px', minHeight: '0', display: 'none'})),
            state('expanded', style({height: '*'})),
            transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)')),
        ]),
    ],
})
export class JobsListComponent implements OnInit {

    dataSource = JOBS;
    expandedJob: Job;
    displayedColumns = ['name', 'date'];

    constructor() { }

    ngOnInit() {
    }

}
