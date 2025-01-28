from typing import Dict, Optional, List, Any, Tuple
import hashlib
import json


class Node:
    """Base class for trie nodes."""
    def hash(self) -> str:
        """Calculate node hash."""
        raise NotImplementedError


class LeafNode(Node):
    """Leaf node containing actual data."""
    def __init__(self, key: bytes, value: bytes):
        self.key = key
        self.value = value
        
    def hash(self) -> str:
        """Calculate leaf node hash."""
        data = self.key + b':' + self.value
        return hashlib.sha256(data).hexdigest()


class BranchNode(Node):
    """Branch node with up to 16 children."""
    def __init__(self):
        self.children: List[Optional[Node]] = [None] * 16
        self.value: Optional[bytes] = None
        
    def hash(self) -> str:
        """Calculate branch node hash."""
        child_hashes = [
            child.hash() if child else hashlib.sha256(b'').hexdigest()
            for child in self.children
        ]
        value_hash = hashlib.sha256(self.value or b'').hexdigest()
        data = ':'.join(child_hashes + [value_hash]).encode()
        return hashlib.sha256(data).hexdigest()


class ExtensionNode(Node):
    """Extension node for shared prefixes."""
    def __init__(self, prefix: bytes, next_node: Node):
        self.prefix = prefix
        self.next_node = next_node
        
    def hash(self) -> str:
        """Calculate extension node hash."""
        data = self.prefix + b':' + self.next_node.hash().encode()
        return hashlib.sha256(data).hexdigest()


class MerklePatriciaTrie:
    """Merkle Patricia Trie implementation for state storage."""
    def __init__(self):
        self.root: Optional[Node] = None
        self.db: Dict[str, bytes] = {}  # Simple key-value store
        
    def _encode_key(self, key: str) -> bytes:
        """Convert key to compact hex encoding."""
        return bytes.fromhex(hashlib.sha256(key.encode()).hexdigest())
        
    def _encode_value(self, value: Any) -> bytes:
        """Encode value to bytes."""
        return json.dumps(value, sort_keys=True).encode()
        
    def _decode_value(self, value: bytes) -> Any:
        """Decode value from bytes."""
        return json.loads(value.decode())
        
    def _get_node_type(self, node: Node) -> str:
        """Get the type of a node."""
        if isinstance(node, LeafNode):
            return 'leaf'
        elif isinstance(node, BranchNode):
            return 'branch'
        elif isinstance(node, ExtensionNode):
            return 'extension'
        raise ValueError('Unknown node type')
        
    def _common_prefix(self, key1: bytes, key2: bytes) -> bytes:
        """Find common prefix between two keys."""
        for i in range(min(len(key1), len(key2))):
            if key1[i] != key2[i]:
                return key1[:i]
        return key1[:min(len(key1), len(key2))]
        
    def put(self, key: str, value: Any) -> None:
        """
        Insert or update a key-value pair.
        
        Args:
            key: Key to store
            value: Value to store
        """
        encoded_key = self._encode_key(key)
        encoded_value = self._encode_value(value)
        
        if not self.root:
            self.root = LeafNode(encoded_key, encoded_value)
            return
            
        self.root = self._put_node(self.root, encoded_key, encoded_value)
        
    def _put_node(self, node: Node, key: bytes, value: bytes) -> Node:
        """Recursive helper for put operation."""
        node_type = self._get_node_type(node)
        
        if node_type == 'leaf':
            leaf_node = node
            if key == leaf_node.key:
                return LeafNode(key, value)
                
            # Create branch node
            common = self._common_prefix(key, leaf_node.key)
            branch = BranchNode()
            
            # Insert existing leaf
            branch.children[leaf_node.key[len(common)] & 0xF] = LeafNode(
                leaf_node.key[len(common) + 1:],
                leaf_node.value
            )
            
            # Insert new leaf
            branch.children[key[len(common)] & 0xF] = LeafNode(
                key[len(common) + 1:],
                value
            )
            
            if common:
                return ExtensionNode(common, branch)
            return branch
            
        elif node_type == 'extension':
            extension_node = node
            common = self._common_prefix(key, extension_node.prefix)
            
            if len(common) == len(extension_node.prefix):
                # Prefix fully matches, continue with next node
                extension_node.next_node = self._put_node(
                    extension_node.next_node,
                    key[len(common):],
                    value
                )
                return extension_node
                
            # Split extension node
            branch = BranchNode()
            if len(extension_node.prefix) > len(common):
                # Part of original prefix becomes new extension
                branch.children[extension_node.prefix[len(common)] & 0xF] = ExtensionNode(
                    extension_node.prefix[len(common) + 1:],
                    extension_node.next_node
                )
                
            # Insert new leaf
            branch.children[key[len(common)] & 0xF] = LeafNode(
                key[len(common) + 1:],
                value
            )
            
            if common:
                return ExtensionNode(common, branch)
            return branch
            
        else:  # Branch node
            branch_node = node
            if not key:
                branch_node.value = value
                return branch_node
                
            index = key[0] & 0xF
            child = branch_node.children[index]
            
            if child:
                branch_node.children[index] = self._put_node(
                    child,
                    key[1:],
                    value
                )
            else:
                branch_node.children[index] = LeafNode(key[1:], value)
                
            return branch_node
            
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value by key.
        
        Args:
            key: Key to look up
            
        Returns:
            Value if found, None otherwise
        """
        if not self.root:
            return None
            
        encoded_key = self._encode_key(key)
        node, remaining_key = self._get_node(self.root, encoded_key)
        
        if not node or remaining_key:
            return None
            
        if isinstance(node, LeafNode):
            return self._decode_value(node.value)
        elif isinstance(node, BranchNode) and node.value:
            return self._decode_value(node.value)
            
        return None
        
    def _get_node(self, node: Node, key: bytes) -> Tuple[Optional[Node], bytes]:
        """Recursive helper for get operation."""
        node_type = self._get_node_type(node)
        
        if node_type == 'leaf':
            leaf_node = node
            if key == leaf_node.key:
                return leaf_node, b''
            return None, key
            
        elif node_type == 'extension':
            extension_node = node
            if key.startswith(extension_node.prefix):
                return self._get_node(
                    extension_node.next_node,
                    key[len(extension_node.prefix):]
                )
            return None, key
            
        else:  # Branch node
            branch_node = node
            if not key:
                return branch_node, b''
                
            index = key[0] & 0xF
            child = branch_node.children[index]
            
            if child:
                return self._get_node(child, key[1:])
            return None, key
            
    def delete(self, key: str) -> bool:
        """
        Delete a key-value pair.
        
        Args:
            key: Key to delete
            
        Returns:
            bool: True if key was deleted
        """
        if not self.root:
            return False
            
        encoded_key = self._encode_key(key)
        new_root, deleted = self._delete_node(self.root, encoded_key)
        
        if deleted:
            self.root = new_root
            return True
        return False
        
    def _delete_node(self, node: Node, key: bytes) -> Tuple[Optional[Node], bool]:
        """Recursive helper for delete operation."""
        node_type = self._get_node_type(node)
        
        if node_type == 'leaf':
            leaf_node = node
            return None, key == leaf_node.key
            
        elif node_type == 'extension':
            extension_node = node
            if not key.startswith(extension_node.prefix):
                return node, False
                
            new_next, deleted = self._delete_node(
                extension_node.next_node,
                key[len(extension_node.prefix):]
            )
            
            if not deleted:
                return node, False
                
            if not new_next:
                return None, True
                
            if isinstance(new_next, ExtensionNode):
                # Merge extension nodes
                return ExtensionNode(
                    extension_node.prefix + new_next.prefix,
                    new_next.next_node
                ), True
                
            return ExtensionNode(extension_node.prefix, new_next), True
            
        else:  # Branch node
            branch_node = node
            if not key:
                if not branch_node.value:
                    return node, False
                    
                branch_node.value = None
                return self._normalize_branch(branch_node), True
                
            index = key[0] & 0xF
            child = branch_node.children[index]
            
            if not child:
                return node, False
                
            new_child, deleted = self._delete_node(child, key[1:])
            
            if not deleted:
                return node, False
                
            branch_node.children[index] = new_child
            return self._normalize_branch(branch_node), True
            
    def _normalize_branch(self, node: BranchNode) -> Optional[Node]:
        """
        Normalize a branch node after deletion.
        
        If branch node has only one child, convert it to extension node.
        If branch node has no children and no value, return None.
        """
        # Count non-None children
        children = [i for i, child in enumerate(node.children) if child]
        
        if not children:
            return None if not node.value else node
            
        if len(children) == 1 and not node.value:
            # Convert to extension node
            index = children[0]
            child = node.children[index]
            
            if isinstance(child, LeafNode):
                return LeafNode(bytes([index]) + child.key, child.value)
                
            if isinstance(child, ExtensionNode):
                return ExtensionNode(
                    bytes([index]) + child.prefix,
                    child.next_node
                )
                
            return ExtensionNode(bytes([index]), child)
            
        return node
        
    def get_proof(self, key: str) -> List[Dict[str, Any]]:
        """
        Generate Merkle proof for a key.
        
        Args:
            key: Key to generate proof for
            
        Returns:
            List of proof elements
        """
        if not self.root:
            return []
            
        proof = []
        encoded_key = self._encode_key(key)
        self._get_proof_node(self.root, encoded_key, proof)
        return proof
        
    def _get_proof_node(self, node: Node, key: bytes, proof: List[Dict[str, Any]]) -> bool:
        """Recursive helper for proof generation."""
        node_type = self._get_node_type(node)
        proof_element = {
            'type': node_type,
            'hash': node.hash()
        }
        
        if node_type == 'leaf':
            leaf_node = node
            proof_element.update({
                'key': leaf_node.key.hex(),
                'value': self._decode_value(leaf_node.value)
            })
            proof.append(proof_element)
            return key == leaf_node.key
            
        elif node_type == 'extension':
            extension_node = node
            proof_element.update({
                'prefix': extension_node.prefix.hex()
            })
            proof.append(proof_element)
            
            if key.startswith(extension_node.prefix):
                return self._get_proof_node(
                    extension_node.next_node,
                    key[len(extension_node.prefix):],
                    proof
                )
            return False
            
        else:  # Branch node
            branch_node = node
            proof_element.update({
                'value': self._decode_value(branch_node.value) if branch_node.value else None,
                'children': [
                    child.hash() if child else None
                    for child in branch_node.children
                ]
            })
            proof.append(proof_element)
            
            if not key:
                return branch_node.value is not None
                
            index = key[0] & 0xF
            child = branch_node.children[index]
            
            if child:
                return self._get_proof_node(child, key[1:], proof)
            return False
            
    def verify_proof(self, key: str, value: Any, proof: List[Dict[str, Any]]) -> bool:
        """
        Verify a Merkle proof.
        
        Args:
            key: Key to verify
            value: Expected value
            proof: Proof elements
            
        Returns:
            bool: True if proof is valid
        """
        if not proof:
            return False
            
        encoded_key = self._encode_key(key)
        encoded_value = self._encode_value(value)
        
        try:
            current_key = encoded_key
            
            for element in proof:
                element_type = element['type']
                
                if element_type == 'leaf':
                    if current_key != bytes.fromhex(element['key']):
                        return False
                        
                    leaf_value = self._encode_value(element['value'])
                    if leaf_value != encoded_value:
                        return False
                        
                    leaf = LeafNode(
                        bytes.fromhex(element['key']),
                        leaf_value
                    )
                    if leaf.hash() != element['hash']:
                        return False
                        
                elif element_type == 'extension':
                    prefix = bytes.fromhex(element['prefix'])
                    if not current_key.startswith(prefix):
                        return False
                        
                    current_key = current_key[len(prefix):]
                    
                elif element_type == 'branch':
                    if not current_key:
                        if element['value'] != value:
                            return False
                    else:
                        index = current_key[0] & 0xF
                        if not element['children'][index]:
                            return False
                        current_key = current_key[1:]
                        
                else:
                    return False
                    
            return True
            
        except (KeyError, ValueError):
            return False 