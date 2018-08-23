import { Injectable } from '@angular/core';
import { AngularFireAuth } from 'angularfire2/auth';
import { auth, User } from 'firebase/app';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    constructor(public fireAuth: AngularFireAuth) {
        this.user = fireAuth.user;
    }
    user: Observable<User | null>;
    login() {
        this.fireAuth.auth.signInWithPopup(new auth.GoogleAuthProvider());
    }
    logout() {
        this.fireAuth.auth.signOut();
    }
}
