import jax
import jax.numpy as jnp
from jax import jit

# VQE LOSSES
def vqe_fidelties(Y, params, q_circuit):
    def vqe_fidelty(y, p, q_circuit):
        psi_out = q_circuit(p)
        
        return jnp.square(jnp.abs(jnp.conj(psi_out) @  y))
    
    v_fidelty = jax.vmap(lambda y, p: vqe_fidelty(y,p,q_circuit), in_axes = (0, 0) )

    return jnp.mean(v_fidelty(Y, params))

def vqe_fidelties_neighbouring(states):
    def vqe_fidelty(s1, s2):
        return jnp.square(jnp.abs(jnp.conj(s1) @  s2))
    
    v_fidelty = jax.vmap(lambda s1, s2: vqe_fidelty(s1,s2), in_axes = (0, 0) )

    
    return jnp.mean(v_fidelty(states[:-1], states[1:]))

# QCNN LOSSES
def cross_entropy(X, Y, params, q_circuit):
    v_qcnn_prob = jax.vmap(lambda v: q_circuit(v, params))

    predictions = v_qcnn_prob(X)
    logprobs = jnp.log(predictions)

    nll = jnp.take_along_axis(logprobs, jnp.expand_dims(Y, axis=1), axis=1)
    ce = -jnp.mean(nll)

    return ce

def cross_entropy_multiclass(X, Y, params, q_circuit):
    v_qcnn_prob = jax.vmap(lambda v: q_circuit(v, params))

    predictions = v_qcnn_prob(X)
    logprobs = jnp.log(predictions)
    Y = Y.flatten()
    logprobs = (jnp.reshape(logprobs.flatten(), (len(Y),2)))

    nll = jnp.take_along_axis(logprobs, jnp.expand_dims(Y, axis=1), axis=1)
    ce = - jnp.mean(nll)
    
    return ce

def hinge(X, Y, params, q_circuit):
    v_qcnn_prob = jax.vmap(lambda v: q_circuit(v, params))

    predictions = 2*v_qcnn_prob(X) - 1 
    Y_hinge     = 2*Y - 1
    
    hinge_loss = jnp.mean(1 - predictions[:,1]*Y_hinge)
    
    return hinge_loss