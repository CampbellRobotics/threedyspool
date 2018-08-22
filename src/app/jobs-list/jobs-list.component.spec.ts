import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { JobsList2Component } from './jobs-list2.component';

describe('JobsList2Component', () => {
  let component: JobsList2Component;
  let fixture: ComponentFixture<JobsList2Component>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ JobsList2Component ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(JobsList2Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
