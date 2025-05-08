import React, { createContext, useState, useEffect } from 'react';
import firebase from './firebase';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = firebase.auth().onAuthStateChanged(async (user) => {
      if (user) {
        // Check if user is admin
        const userDoc = await firebase.firestore().collection('users').doc(user.uid).get();
        const userData = userDoc.data();
        
        setCurrentUser(user);
        setIsAdmin(userData?.role === 'admin');
      } else {
        setCurrentUser(null);
        setIsAdmin(false);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const login = async (email, password) => {
    return firebase.auth().signInWithEmailAndPassword(email, password);
  };

  const register = async (email, password, name) => {
    const result = await firebase.auth().createUserWithEmailAndPassword(email, password);
    await firebase.firestore().collection('users').doc(result.user.uid).set({
      name,
      email,
      role: 'user',
      createdAt: firebase.firestore.FieldValue.serverTimestamp()
    });
    return result;
  };

  const logout = () => {
    return firebase.auth().signOut();
  };

  const value = {
    currentUser,
    isAdmin,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};