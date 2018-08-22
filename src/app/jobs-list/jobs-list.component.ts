import {Component, OnInit} from '@angular/core';
import {animate, state, style, transition, trigger} from '@angular/animations';
import { JOBS } from '../mock-jobs';
import { Job } from '../job';

/**
 * @title Jobs list with expandable rows
 */
@Component({
  selector: 'app-jobs-list',
  styleUrls: ['jobs-list.component.css'],
  templateUrl: 'jobs-list.component.html',
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
  columnsToDisplay = ['name', 'date'];
  expandedJob: Job;

  constructor () {}

  ngOnInit () {}
}
