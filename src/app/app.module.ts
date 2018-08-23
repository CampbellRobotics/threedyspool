import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';

import { MatTableModule, MatToolbarModule, MatButtonModule } from '@angular/material';

import { MomentModule } from 'ngx-moment';

import { AppComponent } from './app.component';
import { JobsListComponent } from './jobs-list/jobs-list.component';
import { AuthService } from './services/auth.service';
import { LoginButtonComponent } from './login-button/login-button.component';
import { AngularFireModule } from 'angularfire2';
import { AngularFireAuthModule } from 'angularfire2/auth';
import { environment } from '../environments/environment';

@NgModule({
    declarations: [
        AppComponent,
        JobsListComponent,
        LoginButtonComponent,
    ],
    imports: [
        BrowserModule,
        BrowserAnimationsModule,
        AngularFireModule.initializeApp(environment.firebase, 'threedyspool'),
        AngularFireAuthModule,
        MomentModule,
        MatTableModule,
        MatToolbarModule,
        MatButtonModule,
    ],
    providers: [AuthService],
    bootstrap: [AppComponent]
})
export class AppModule { }
