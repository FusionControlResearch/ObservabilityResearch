# Fixed closed-loop observability-aware recovery demo
# Forces observability collapse and demonstrates recovery via probing

import numpy as np
import matplotlib.pyplot as plt
import csv

# Time setup
T = 150
t = np.arange(T)

# State: [Ip, li, beta, gamma]
x = np.zeros((T, 6))
x[0] = [10.0, 1.0, 2.0, 0.1, 0.0, 0.0]
Ip_0 = 10.0
li_0 = 1.0

dt = 1.0

obs_integrator = 0.0

n = 2

a_obs = 0.01
b = 0.5
c = 0.3
d_probe = 0.05
probe_integrator = 0.0

alpha = 1e-3           # initial estimator confidence

P = alpha * np.eye(n)  # <-- THIS IS P_0
u_max = 0.1   # e.g. allow ±10% max probing

# Control: [Vloop, Paux]
u = np.zeros((T, 2))
u[:, 0] = 1.0      # loop voltage
u[:, 1] = 1.0      # heating

# Parameters
a, c_nom, d, e, f = 0.8, 0.3, 0.2, 0.5, 0.3
alpha1, alpha2, alpha3, alpha4 = 1.0, 0.5, 0.25, 0.15

# Tracking
L_obs = np.zeros(T)
L_obs_nom = np.zeros(T)
probing = np.zeros(T)

L_tilde = 0.0


#L_buffer = []
rho_buffer = []
P_history = []
li_buffer = []
beta_buffer = []
Ip_buffer = []


mag_trigger = False
rate_trigger = False
rank_trigger = False
correction = False

# Observability matrix
def compute_G(Ip, li, beta, c_eff):
    return np.array([
        [alpha1*a + alpha2*c_eff,   -alpha2*d],
        [alpha3*beta*a,             alpha3*e*(Ip - Ip_0)],
        [alpha4*beta*a,                       alpha4*f*(li - li_0)]
    ])


rho_nominal = []
P_max = 1.0
L_nominal = 0.0

k_Ip   = 0.02
k_beta = 0.03
k_li   = 0.02


Ip_nominal = 0.0
li_nominal = 0.0
beta_nominal = 0.0

# probe effectiveness state
z = 0.0
tau = 20.0   # recovery time constant (steps)

#W = 30
T_warmup = 50  # timesteps
warmup = True
certified = False

n_sigma = 2

for k in range(T-1):

    Ip, li, beta, gamma, gamma_dot, obs_integrator = x[k]

    # Degradation window
    degraded = (60 < k < 120)

    # Loss of actuator coupling
    if degraded:
        c_eff = 0.0
    else:
        c_eff = c_nom

    # Pressure erosion
    if degraded:
        beta_measured = beta * 0.6
    else:
        beta_measured = beta


    # Observability metric
    G_eff = compute_G(Ip, li, beta_measured, c_eff)
    L_obs[k] = np.log(1 + np.linalg.cond(G_eff))


    # --- ESTIMATOR CONFIDENCE UPDATE (Layer B) ---
    # P inflates when observability degrades
    P = beta_measured * L_obs[k] * np.eye(n)
    # Frobenius norm (used for certification only)
    P_norm = np.linalg.norm(P, ord='fro')


    if k < T_warmup:
        certified = False
        probe = False
        P_history.append(P_norm)
        s = np.linalg.svd(G_eff, compute_uv=False)
        #L_buffer.append(L_obs)
        li_buffer.append(li)
        beta_buffer.append(beta_measured)
        Ip_buffer.append(Ip)
        rho = s[-1] / s[0]
        rho_buffer.append(rho)
        rho_nominal.append(s[-1] / s[0])
    elif k == T_warmup:
        warmup = False
        P_nominal = np.mean(P_history[:T_warmup])
        li_nominal = np.mean(li_buffer[:T_warmup])
        beta_nominal = np.mean(beta_buffer[:T_warmup])
        Ip_nominal = np.mean(Ip_buffer[:T_warmup])
        L_ref = np.mean(L_obs[:T_warmup])
        L_std = np.std(L_obs[:T_warmup])
        L_high = L_ref + n_sigma * L_std
        #L_low  = L_ref + m_sigma * L_std

    if warmup is False:
        if P_norm < 1.2 * P_nominal: #and (abs(u_k - 1.0) < 0.6 * u_max):
            if certified is False:
                certified = True
                P_nominal = np.mean(P_history[:T_warmup])
                #L_nominal = np.mean(L_obs[k-1:k])
                #L_std     = np.std(L_obs[k-1:k])
                #L_tilde_nominal = L_obs[k-1:k] / L_nominal
                L_nominal = np.mean(L_obs[:T_warmup])
                L_std     = np.std(L_obs[:T_warmup])
                L_tilde_nominal = L_obs[:T_warmup] / L_nominal
                dL_nominal = np.diff(L_tilde_nominal) / T_warmup#(k - (k-1))
                dL_std = np.std(dL_nominal)
                rho_mean   = np.mean(rho_buffer)
                rho_std    = np.std(rho_buffer)
                #L_high = 1.0 + (3*(L_std/L_nominal))


    if certified is True:
        L_tilde_prev = L_tilde
        L_tilde = L_obs[k] / L_nominal
        dL = (L_tilde - L_tilde_prev) / (k - (k-1))
        mag_trigger = L_tilde > 1.0 + (n_sigma*(L_std/L_nominal))
        rate_trigger = abs(dL) > 3*dL_std
        s = np.linalg.svd(G_eff, compute_uv=False)
        rho = s[-1] / s[0]
        rank_trigger = rho < (rho_mean - 3*rho_std)

    
    if k == 60:
        # healthy indices: after warm-up, before degradation
        healthy_idx = np.arange(50, 60)
        mu_healthy    = np.mean(L_obs[healthy_idx])
        sigma_healthy = np.std(L_obs[healthy_idx])
        L_high_nom = mu_healthy + n_sigma * sigma_healthy
    
    #if k >= 60:
    #    L_obs_nom[k] = (L_obs[k] - mu_healthy) / sigma_healthy



    #if (mag_trigger or rate_trigger or rank_trigger) and certified is True:
    '''if (mag_trigger or rank_trigger) and certified is True:
        probe = True
        probing[k] = 1.0
        c_eff = c_nom
        u[k, 1] = 0.03 
        probe_amp = 1.03
        u_k = 1.03
        z = z + (probe_amp - z) / tau
    else:
        probe = False
        probing[k] = 0.0
        u[k, 1] = 0.0
        u_k = 1.0
        probe_amp = 1.0
        z = z - z / tau'''

    probe = False
    u[k, 1] = 0.0
    u_k = 1.0
    probe_amp = 1.0
    z = z - z / tau
    probing[k] = 0.0

    Ip_next = Ip + (a*u[k,1] - 0.12*(Ip-10.0))
    li_next = li + (c_eff*u[k,1] - d*(li-1.0))
    #Ip_next = Ip + (a*u[k,1] - 0.12*(Ip))
    #li_next = li + (c_eff*u[k,1] - d*(li))
    beta_eq = 2.0
    k_beta = 0.08

    beta_next = beta_measured + (e*u[k,1] - k_beta*(beta_measured - beta_eq))
    
    if warmup is True or certified is False:
        gamma_dot = 0.0
        x[k+1] = [Ip_next, li_next, beta_next, gamma, gamma_dot, obs_integrator]
    else:
        gamma_dot = a_obs * gamma + b * obs_integrator * (1 - c * probing[k])
        gamma_next = max(0.0, gamma + gamma_dot)
        obs_integrator_next = obs_integrator + max(0, L_obs[k] - L_nominal)
        x[k+1] = [Ip_next, li_next, beta_next, gamma_next, gamma_dot, obs_integrator_next]
    
    

# Final observability
G_final = compute_G(x[-1,0], x[-1,1], x[-1,2], c_nom)
L_obs[-1] = np.log(np.linalg.cond(G_final.T @ G_final))
print(np.mean(L_obs))




# Plots
plt.figure()
plt.plot(t, L_obs)
plt.ylabel("Observability loss L_obs")
plt.xlabel("time")
plt.title("Observability collapse and recovery")
plt.axhline(y=L_high, color='green', linestyle='-')
plt.fill_between(
    range(len(probing)),
    max(L_obs),
    min(L_obs),
    where=probing > 0,
    alpha=0.2,
    label="Probing active"
)
plt.legend
plt.show()

#with open('L_obs_data_probe.csv', 'w', newline='') as myfile:
with open('L_obs_nom_sigma4.csv', 'w', newline='') as myfile:
    writer = csv.writer(myfile)
    writer.writerow(['x_value', 'y_value']) # Write header
    for i in range(len(t)):
        writer.writerow([t[i], L_obs[i]]) # Write data rows

'''plt.figure()
plt.plot(t, L_obs_nom)
plt.ylabel("Nominal Observability loss L_obs_nom")
plt.xlabel("time")
plt.title("Nominal Observability collapse and recovery")
plt.axhline(y=L_high_nom, color='green', linestyle='-')
plt.show()

with open('L_obs_nom_data_no_probe.csv', 'w', newline='') as myfile:
    writer = csv.writer(myfile)
    writer.writerow(['x_value', 'y_value']) # Write header
    for i in range(len(t)):
        writer.writerow([t[i], L_obs_nom[i]]) # Write data rows'''

plt.figure()
plt.plot(t, probing)
plt.ylabel("Probing active")
plt.xlabel("time")
plt.title("Supervisor-triggered probing")
plt.show()

with open('probe_on_data.csv', 'w', newline='') as myfile:
    writer = csv.writer(myfile)
    writer.writerow(['x_value', 'y_value']) # Write header
    for i in range(len(t)):
        writer.writerow([t[i], probing[i]]) # Write data rows

plt.figure()
plt.plot(t, x[:,3])
plt.axhline(1.0, linestyle="--")
plt.ylabel("Estimated gamma")
plt.xlabel("time")
plt.title("Observability Change Before and After Disruption")
plt.show()

with open('gamma_data_no_probe.csv', 'w', newline='') as myfile:
    writer = csv.writer(myfile)
    writer.writerow(['x_value', 'y_value']) # Write header
    for i in range(len(t)):
        writer.writerow([t[i], x[i, 3]]) # Write data rows

sensor_levels = np.linspace(1.0, 0.2, 25)
L_test = []

for s in sensor_levels:

    beta_measured_test = beta * s
    
    G = compute_G(Ip, li, beta_measured_test, c_nom)
    cond = np.linalg.cond(G)
    
    L = np.log(1 + cond)
    L_test.append(L)

plt.figure()
plt.plot(sensor_levels, L_test)
plt.xlabel("Sensor quality")
plt.ylabel("Observability loss L_obs")
plt.title("Observability metric sensitivity to diagnostic degradation")
plt.gca().invert_xaxis()
plt.show()



#--------------------------------------------------------------------------------------------

'''x[:,0] = Ip
x[:,1] = li
x[:,2] = beta

plt.figure()

plt.plot(
    x_no_probe[:,0],
    x_no_probe[:,2],
    label="No probing",
    linewidth=2
)

plt.plot(
    x_probe[:,0],
    x_probe[:,2],
    label="Observability probing",
    linewidth=2
)

plt.xlabel("Plasma current (Ip)")
plt.ylabel("Plasma beta")

plt.title("State-space trajectory under observability degradation")

plt.legend()

plt.show()


#---------------------------------------------------------------------------------------------

probe_indices = np.where(probe_hist == 1)[0]

plt.scatter(
    x_probe[probe_indices,0],
    x_probe[probe_indices,2],
    s=20,
    label="Probing active"
)

#-----------------------------------------------------------------------------------------------

plt.scatter(
    x_probe[:,0],
    x_probe[:,2],
    c=L_probe,
    cmap="viridis",
    s=10
)

plt.colorbar(label="Observability loss L_obs")


Figure X shows the state-space trajectory of the simulated plasma dynamics in the 
(
𝐼
𝑝
,
𝛽
)
(I
p
	​

,β) plane. In the absence of probing, the system drifts toward regions associated with elevated observability loss. When the proposed observability probing mechanism is enabled, small excitation inputs alter the trajectory, preventing prolonged residence in poorly observable regions. Points where probing is active are highlighted. This visualization illustrates the geometric mechanism by which the proposed supervisory layer restores system observability.'''