import copy
import math
import numpy as np


def diffusion_distance(dcoordinates1, dcoordinates2, eigenvalues, k, time=0.0):
    """Compute the diffusion distance from diffusion coordinates and eigenvalues"""

    dcoordinates1=dcoordinates1[:k]
    dcoordinates2=dcoordinates2[:k]
    exp_eigenvalues=np.exp(-2*eigenvalues[:k]*time)

    dist=exp_eigenvalues*np.square(dcoordinates1-dcoordinates2)
    return np.sum(dist)


def rmsd_rotation(coordinates1, coordinates2):
    """Compute the rotation matrix to optimally align mol2 to mol1."""
    
    u = coordinates1.reshape((-1, 3))
    v = coordinates2.reshape((-1, 3))

    cov = np.dot(u.transpose(), v)
    [U, S, Vt] = np.linalg.svd(cov)

    if np.linalg.det(U) * np.linalg.det(Vt) < 0:
        # Invert the coordinate assocated with the least singular
        # value.  

        # It's ok to have inversion of 2 coordinates(it's just a 180
        # degree rotation), but not 3 or 1.  Inverting the
        # transformation associated with the least singular value will
        # give the least possible increase in RMSD.
        for idx in xrange(3):
            Vt[2, idx] = -Vt[2, idx]

    # Optimally align v and u.
    return np.dot(Vt.transpose(), U.transpose()), 0


def center_of_geometry(coordinates):
    coords = coordinates.reshape((-1, 3))
    cog = np.array([0.0, 0.0, 0.0])
    num_atom = coords.shape[0]
    for idx in xrange(num_atom):
        cog = cog + coords[idx]

    cog = cog / num_atom

    return cog


def rmsd(coordinates1, coordinates2):
    """Compute the RMSD distance between the two molecules."""

    coordinates1 = np.array(coordinates1)
    coordinates2 = np.array(coordinates2)

    coord1 = translate(coordinates1, -center_of_geometry(coordinates1))
    coord2 = translate(coordinates2, -center_of_geometry(coordinates2))

    u = coord1.reshape((-1, 3))
    v = coord2.reshape((-1, 3))
    cov = np.dot(u.transpose(), v)
    s = np.linalg.svd(cov, compute_uv=0)


    if np.linalg.det(cov) < 0.:
        s[2] = -s[2]

    num_atoms = u.shape[0]
    rmsd = abs(np.dot(coord1, coord1) + np.dot(coord2, coord2) - 2. * np.sum(s))/num_atoms

    if rmsd < 0.:
        if abs(rmsd) < 1e-7:
            rmsd = abs(rmsd)
    return np.sqrt(rmsd)


def translate(coordinates, translation_vector):
    """Translate each atom in  molecule by adding the translation vector."""

    coords = coordinates.reshape((-1, 3))
    for idx in xrange(len(coords)):
        coords[idx] = tuple(coords[idx] + translation_vector)

    return coords.reshape((-1, ))

def flat_rmsd(coordinates1, coordinates2):
    """Return unminimized rmsd."""

    u = coordinates1.reshape((-1, 3))
    v = coordinates2.reshape((-1, 3))

    num_atoms = u.shape[0]
    s = sum((np.linalg.norm(u[idx] - v[idx]) ** 2 for idx in xrange(num_atoms)))
    return math.sqrt(s / num_atoms)


def dihedral(x, i1, i2, i3, i4):

    radian = 180./math.pi

    xa = x[3 * (i1 - 1)]
    xb = x[3 * (i2 - 1)]
    xc = x[3 * (i3 - 1)]
    xd = x[3 * (i4 - 1)]
    ya = x[3 * (i1 - 1) + 1]
    yb = x[3 * (i2 - 1) + 1]
    yc = x[3 * (i3 - 1) + 1]
    yd = x[3 * (i4 - 1) + 1]
    za = x[3 * (i1 - 1) + 2]
    zb = x[3 * (i2 - 1) + 2]
    zc = x[3 * (i3 - 1) + 2]
    zd = x[3 * (i4 - 1) + 2]
    
    xba = xb - xa
    yba = yb - ya
    zba = zb - za
    xcb = xc - xb
    ycb = yc - yb
    zcb = zc - zb
    xdc = xd - xc
    ydc = yd - yc
    zdc = zd - zc

    xt = yba*zcb - ycb*zba
    yt = xcb*zba - xba*zcb
    zt = xba*ycb - xcb*yba

    xu = ycb*zdc - ydc*zcb
    yu = xdc*zcb - xcb*zdc
    zu = xcb*ydc - xdc*ycb

    rt = math.sqrt(xt*xt + yt*yt + zt*zt)
    ru = math.sqrt(xu*xu + yu*yu + zu*zu)

    xt = xt/rt
    yt = yt/rt
    zt = zt/rt

    xu = xu/ru
    yu = yu/ru
    zu = zu/ru

    rcb = math.sqrt(xcb*xcb + ycb*ycb + zcb*zcb)

    xcb = xcb/rcb
    ycb = ycb/rcb
    zcb = zcb/rcb

    xq = yt*zcb - ycb*zt 
    yq = xcb*zt - xt*zcb 
    zq = xt*ycb - xcb*yt 

    x = xt*xu + yt*yu + zt*zu
    y = xq*xu + yq*yu + zq*zu

    dihed = -radian*math.atan2(y,x)

    return dihed


def atom_dist(mol, idx, jdx):
    natom = len(mol)/3
    return np.linalg.norm(np.array(mol[3*(idx-1):3*idx]) - np.array(mol[3*(jdx-1):3*jdx]))

def phi(q):
    return dihedral(q, 5, 7, 9, 15)

def psi(q):
    return dihedral(q, 7, 9, 15, 17)

def ome1(q):
    return dihedral(q, 2,  5,  7,  9)

def ome2(q):
    return dihedral(q, 9, 15, 17, 19)

def dphi(q, wq):

    wq_mag = np.linalg.norm(wq)
    phi_val = phi(q)
    dq = 1.e-7

    qdel = wq * dq / wq_mag
    qdel_mag = np.linalg.norm(qdel)
    phid_val = phi(q + qdel)

    dphi_val = (phid_val - phi_val) / qdel_mag

    return dphi_val


def dpsi(q, wq):

    wq_mag = np.linalg.norm(wq)
    psi_val = psi(q)
    dq = 1.e-7

    qdel = wq * dq / wq_mag
    qdel_mag = np.linalg.norm(qdel)
    psid_val = psi(q + qdel)

    dpsi_val = (psid_val - psi_val) / qdel_mag

    return dpsi_val

