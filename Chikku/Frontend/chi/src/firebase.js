// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getFirestore } from "firebase/firestore";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "firebase/auth";
import { collection, addDoc, getDocs, query, where, doc, getDoc, setDoc, updateDoc, deleteDoc, serverTimestamp } from "firebase/firestore";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAKENwyOHD2NHlkTJiLEKV8w_LsK5zjs40",
  authDomain: "rahul-c3bb9.firebaseapp.com",
  projectId: "rahul-c3bb9",
  storageBucket: "rahul-c3bb9.firebasestorage.app",
  messagingSenderId: "624168823701",
  appId: "1:624168823701:web:7f2a67051be3266d1ce49c",
  measurementId: "G-8DW845PB3S"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const db = getFirestore(app);
const auth = getAuth(app);

// Export everything needed
export { 
  app, 
  db, 
  auth, 
  analytics,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  collection, 
  addDoc, 
  getDocs, 
  query, 
  where, 
  doc, 
  getDoc, 
  setDoc, 
  updateDoc, 
  deleteDoc, 
  serverTimestamp 
};
