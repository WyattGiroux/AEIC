# Derivation Of Two Degree-Of-Freedom Segments
For an aircraft flying at speed $u_0$ and altitude $h$ with flight angle $\gamma$ and angle of attack $\alpha$, the unsteady equations of motion can be written as:

$$
m\dot u_0 = F_n\cos\alpha - D - mg\sin\gamma
$$

$$
mu_0\dot\gamma = L + F_n\sin\alpha - mg\cos\gamma
$$

$$
\dot h = u_0\sin\gamma
$$

$$
\dot x = u_0\cos\gamma
$$

This derivation assumes the direction of thrust and pitch of the aircraft relative to horizontal are equal and that the wing incidence angle relative to the aircraft body is pre-accounted for in the full vehicle aerodynamics. Combining the equations, we get:

$$
mu_0\dot u_0 = u_0(F_n\cos\alpha - D) - mg\dot h
$$

$$
mu_0^2\dot\gamma = u_0L + u_0F_n\sin\alpha - mg\dot x
$$

We know $\dot x = \sqrt{u_0^2 - \dot h^2}$. In addition, we assume the aircraft is flying with constant flight angle such that $\dot\gamma = 0$. This leaves:

$$
mu_0\dot u_0 = u_0(F_n\cos\alpha - D) - mg\dot h
$$

$$
mg\sqrt{u_0^2 - \dot h^2} = u_0(L + F_n\sin\alpha)
$$

The first equation can be rearranged to obtain the total-energy equation used by the BADA databases [[@zotero-item-2436]], with the addition of the angle of attack component, which they take to be small:

$$
u_0(F_n\cos\alpha - D) = mg\dot h + mu_0\dot u_0
$$

However, we can rearrange the second equation above by writing $L=D(L/D)$ and substituting for drag power ($u_0D$):

$$
	u_0F_n\cos\alpha - \bigg( \frac{mg}{L/D}\dot x - \frac{1}{L/D}u_0F_n\sin\alpha \bigg) = mg\dot h + mu_0\dot u_0
$$

This simplifies to:

$$
mg\bigg( \dot h + \frac{u_0}{g}\dot u_0  + \frac{\dot x}{L/D}\bigg) = F_nu_0\bigg( \cos\alpha + \frac{\sin\alpha}{L/D} \bigg)
$$

$$
\frac{F_n}{mg} = \frac{\dot h/u_0 + \frac{1}{L/D}\dot x/u_0 + \dot u_0/g}{\cos\alpha + \frac{1}{L/D}\sin\alpha}
$$

where

$$
\dot x = \sqrt{u_0^2 - \dot h^2}
$$

This form of the equation specifies the thrust-to-weight ratio as a function of $\dot h$, $u_0$, $L/D$, and $\alpha$. However, two of these variables can be discarded by assuming the angle-of-attack is in steady state and the **aircraft is always trimmed to the optimal $\alpha$ for a given speed**. In addition, $L/D$ is a function of $\alpha$ and speed. From this, we assume that a given speed at a known altitude sets the aircraft trim and thus the equilibrium angle of attack. The angle of attack and speed uniquely define the aerodynamic performance, meaning the thrust-to-weight equation is effectively:

$$
\boxed{\frac{F_n}{mg} = \frac{\dot h/u_0 + f_1(\dot h, u_0) + \dot u_0/g}{f_2(u_0)}}
$$

This equation tells us that, under the assumptions made of optimal trim and steady pitch angle, the state of the aircraft is fully specified by **two variables** (ROC and TAS in this case). If a performance model supports different trim settings, this would have to be expanded to three variables (baseline variables would be throttle, pitch, trim). However, this could be rearranged to solve for any variable in terms of two other independent variables. This does not need to be constrained to the variables present currently; any relevant variables would be sufficient. Some possible substitutions are given below:

$$
F_n\;\text{ Substitutions:}\quad\quad T_{t4}/T_{t2},\; FAR,\; \text{Throttle},\; PLA, \;...
$$

$$
\dot h\;\text{ Substitutions (incl. Aero): }\quad\quad \gamma,\; L/D,\; C_L,\; C_D
$$

$$
u_0\;\text{(TAS) Substitutions: } \quad\quad CAS,\; IAS,\; GS
$$

While all these variables could be substituted in, it is not immediately clear which choices make sense for an AEIC user to set and, in the case of a standard trajectory, the specific values specified.
