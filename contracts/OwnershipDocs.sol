// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/// @title OwnershipDocs
/// @notice Simple on-chain registry for ownership document metadata (hashes, public keys).
contract OwnershipDocs is Ownable {
    struct Doc {
        uint256 plotId;
        string ownerPublicKey; // off-chain public key or identifier
        string docHash;        // IPFS hash or document fingerprint
        uint256 createdAt;
    }

    mapping(uint256 => Doc) public docs; // plotId => Doc
    uint256[] public docIds;

    event DocIssued(uint256 plotId, string ownerPublicKey, string docHash, uint256 ts);
    event DocEdited(uint256 plotId, string newOwnerPublicKey, string newDocHash, uint256 ts);

    function issueDoc(uint256 plotId, string calldata ownerPublicKey, string calldata docHash) external onlyOwner {
        docs[plotId] = Doc(plotId, ownerPublicKey, docHash, block.timestamp);
        docIds.push(plotId);
        emit DocIssued(plotId, ownerPublicKey, docHash, block.timestamp);
    }

    function editDoc(uint256 plotId, string calldata newOwnerPublicKey, string calldata newDocHash) external onlyOwner {
        docs[plotId] = Doc(plotId, newOwnerPublicKey, newDocHash, block.timestamp);
        emit DocEdited(plotId, newOwnerPublicKey, newDocHash, block.timestamp);
    }

    function getDoc(uint256 plotId) external view returns (Doc memory) {
        return docs[plotId];
    }

    function totalDocs() external view returns (uint256) {
        return docIds.length;
    }
}
