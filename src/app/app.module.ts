import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';

import { MatTableModule } from '@angular/material';

import { MomentModule } from 'ngx-moment';

import { AppComponent } from './app.component';
import { JobsListComponent } from './jobs-list/jobs-list.component';
import { JobsList2Component } from './jobs-list2/jobs-list2.component';

@NgModule({
    declarations: [
        AppComponent,
        JobsListComponent,
        JobsList2Component,
    ],
    imports: [
        BrowserModule,
        BrowserAnimationsModule,
        MomentModule,
        MatTableModule,
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule { }
