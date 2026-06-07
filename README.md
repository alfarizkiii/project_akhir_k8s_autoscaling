# Project Akhir: Kubernetes Autoscaling & Self-Healing dengan FastAPI

**Anggota Kelompok:** 
1. Rachmat Thirdi Maliki (NIM: 235150200111032)
2. Rafi Ananta Nugraha (NIM: 235150200111035)
3. M. Naufal Al Farizki (NIM: 235150207111032)

**Program Studi:** Teknik Informatika, Fakultas Ilmu Komputer (FILKOM), Universitas Brawijaya  

Repositori ini berisi implementasi *deployment microservice* berbasis Python (FastAPI) di atas *cluster* Kubernetes lokal (Minikube). Proyek ini ditujukan untuk mendemonstrasikan kapabilitas ketahanan sistem (*Self-Healing*) dan skalabilitas otomatis (*Horizontal Pod Autoscaler*) dalam arsitektur sistem terdistribusi.

---

## 🚀 Arsitektur Sistem & Komponen
Proyek ini mengimplementasikan arsitektur *cloud-native* dengan komponen-komponen berikut di dalam *namespace* `webapp`:
1. **FastAPI Application:** Aplikasi *backend* yang menyediakan *endpoint* fungsional, *health check*, dan simulasi komputasi intensif untuk uji beban.
2. **ConfigMap & Secret:** Manajemen konfigurasi lingkungan (`development`) dan enkripsi data sensitif (seperti kredensial DB dan API Key) menggunakan *encoding* Base64.
3. **Deployment & Service:** Mengelola replikasi Pod (*default*: 2 replika) dan menyediakan abstraksi jaringan internal (*ClusterIP*).
4. **Horizontal Pod Autoscaler (HPA):** Mekanisme penskalaan dinamis (2 hingga 10 Pod) berdasarkan ambang batas pemakaian CPU (50%) dan Memori (70%).
5. **Ingress NGINX:** Bertindak sebagai *API Gateway* untuk mengarahkan trafik eksternal dari domain lokal `k8s-project.local` ke dalam *cluster*.

---

## 🛠️ Persyaratan Sistem (Prerequisites)
Pastikan sistem lokal (direkomendasikan Linux / WSL2 Ubuntu) telah terpasang *tools* berikut:
* [Docker](https://docs.docker.com/engine/install/)
* [Minikube](https://minikube.sigs.k8s.io/docs/start/) & [kubectl](https://kubernetes.io/docs/tasks/tools/)
* [Git](https://git-scm.com/)
* Alat uji beban `hey`. (Instalasi di Ubuntu: `sudo apt update && sudo apt install hey -y`).

---

## ⚙️ Panduan Instalasi & Eksekusi (Step-by-Step)

### 1. Kloning Repositori
Clone repositori ini ke dalam mesin lokal Anda:
```bash
git clone https://github.com/alfarizkiii/project_akhir_k8s_autoscaling.git
cd project_akhir_k8s_autoscaling
```

2. Inisialisasi Minikube & Addons
Nyalakan cluster Minikube dan aktifkan addons yang dibutuhkan untuk Ingress dan metrik HPA:

```Bash
minikube start
minikube addons enable ingress
minikube addons enable metrics-server
```

3. Build Docker Image Lokal
Arahkan environment terminal ke Docker internal milik Minikube agar cluster bisa membaca image lokal tanpa perlu push ke Docker Hub:

```Bash
eval $(minikube docker-env)
docker build -t fastapi-k8s-app:v1 .
```

4. Deploy Manifest Kubernetes
Terapkan semua konfigurasi objek Kubernetes secara berurutan:

```Bash
kubectl apply -f manifests/
```
Verifikasi bahwa seluruh objek telah berhasil dibuat dan Pod dalam status Running:
```Bash
kubectl get all -n webapp
```
5. Konfigurasi Jaringan & Ekspos Layanan
Tambahkan domain lokal ke dalam file hosts OS lokal Anda:

```Bash
sudo nano /etc/hosts
# Tambahkan baris ini di paling bawah:
# 127.0.0.1 k8s-project.local
```
Buka Terminal Baru, lalu jalankan perintah tunnel untuk mengekspos Ingress ke localhost (biarkan terminal ini tetap menyala):

```Bash
minikube tunnel
```

🧪 Skenario Pengujian
Uji 1: Fungsionalitas & Injeksi Variabel
Lakukan request untuk memastikan aplikasi berjalan dan merespons dengan JSON:

```Bash
curl [http://k8s-project.local/](http://k8s-project.local/)
curl [http://k8s-project.local/secret-info](http://k8s-project.local/secret-info)
```
Uji 2: Load Testing & Autoscaling (HPA)
Buka terminal baru untuk memantau metrik HPA secara real-time:

```Bash
kubectl get hpa -n webapp --watch
```
Di terminal utama, berikan beban trafik tinggi menggunakan hey (1000 request, 100 concurrent):

```Bash
hey -n 1000 -c 100 -t 30 "[http://k8s-project.local/load-test?duration=5&intensity=3000](http://k8s-project.local/load-test?duration=5&intensity=3000)"
```
Ekspektasi: Persentase CPU akan melonjak melampaui 50%, dan HPA akan secara otomatis melakukan scale-up jumlah Pod (Replicas) dari 2 hingga maksimal 10 untuk membagi beban. Setelah trafik selesai, HPA akan melakukan scale-down kembali ke 2 Pod setelah masa tunggu (cooldown) ~5 menit.

Uji 3: Ketahanan Sistem (Self-Healing)
Pantau Pod yang sedang berjalan:

```Bash
kubectl get pods -n webapp --watch
```
Di terminal utama, hapus salah satu Pod secara paksa untuk mensimulasikan crash atau kegagalan node:

```Bash
kubectl delete pod <NAMA-POD> -n webapp
```
Ekspektasi: Deployment Controller Kubernetes akan mendeteksi bahwa jumlah Pod turun di bawah batas minimal (desired state: 2) dan secara instan menciptakan Pod baru untuk memulihkan layanan tanpa downtime yang signifikan.

🧹 Pembersihan (Clean Up)
Jika telah selesai melakukan pengujian, Anda dapat mematikan Minikube untuk membebaskan resource (RAM/CPU) lokal:

```Bash
minikube stop
```
Untuk menghapus cluster secara keseluruhan (opsional):

```Bash
minikube delete
```
