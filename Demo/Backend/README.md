# NestJS Backend - 3D geometry preprocessing and Example Project for Unity Communication

This project contains the **preprocesing system for the point cloud reconstruction and mesh difference preprocessing** and an **example backend application built with NestJS**. It is designed to demonstrate how to structure and implement communication between a backend service and a frontend developed using **Unity** along with the **UnityVueWebGL** library.

## 🎯 Purpose

The main goal of this project is to:

* Serve as a **reference implementation** for backend-to-Unity communication.
* Provide backend support for **3D model preprocessing**, **point cloud reconstruction**, and **heatmap generation**.
* Illustrate how to integrate backend logic with a Unity frontend deployed via WebGL in Vue.js.

## 🗂️ Project Structure

Here's a high-level overview of the most important components of the backend:

```
/src --> nest js application

/externals
  ├── mesh-difference/ --> preprocessing module for heatmap visualization
  │    
  ├── reconstruction/ --> Module to reconstruct a 3d surface from point cloud

/public
  └── models/ --> example models used for the demo
```

## 📌 Key Component: `/externals`

The `/externals` folder contains the **core backend logic scripts** written in Python. These scripts are responsible for the following:

### 🔷 Point Cloud Reconstruction

Located in `/externals/reconstruction`, this set of scripts provides functionality to:

* Reconstruct 3D point clouds from raw sensor or model data.
* Export the result in a format compatible with Unity for WebGL rendering.

More info are available in the README

### 🔶 Heatmap Preprocessing

Found in `/externals/mesh-difference`, these scripts are used to:

* Preprocess 3D model data to prepare for heatmap overlays.

More info are available in the README

## 🔌 Unity Frontend Integration

This backend is meant to be consumed by a **Unity-based WebGL frontend** using the `UnityWebGlVueComponent` framework. It includes:

## 🚀 Getting Started


### Running the Server

```bash
npm run start:dev
```

### Running the Server via Docker

``` bash
docker-compose up
```