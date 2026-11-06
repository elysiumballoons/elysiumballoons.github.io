// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC2981} from "@openzeppelin/contracts/token/common/ERC2981.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";

/// @title Elysium Balloons — 10,000 pixel balloons on Elysium (HYPE L2)
/// @notice Public mint paid in native HYPE. Sequential token IDs 1..10000.
contract ElysiumBalloons is ERC721, ERC2981, Ownable, ReentrancyGuard {
    using Strings for uint256;

    uint256 public constant MAX_SUPPLY = 10_000;

    uint256 public price = 0.01 ether;       // 0.01 HYPE (HYPE has 18 decimals)
    uint256 public maxPerWallet = 100;
    bool public mintOpen;
    uint256 public totalSupply;

    string private _baseTokenURI;
    mapping(address => uint256) public mintedBy;

    event Minted(address indexed to, uint256 firstId, uint256 quantity);

    error MintClosed();
    error BadQuantity();
    error SoldOut();
    error WalletLimit();
    error WrongPayment();
    error WithdrawFailed();

    constructor(string memory baseURI_, address royaltyReceiver)
        ERC721("Elysium Balloons", "EBALLOON")
        Ownable(msg.sender)
    {
        _baseTokenURI = baseURI_;
        _setDefaultRoyalty(royaltyReceiver, 1000); // 10%
    }

    // ------------------------------------------------------------ mint
    function mint(uint256 quantity) external payable nonReentrant {
        if (!mintOpen) revert MintClosed();
        if (quantity == 0) revert BadQuantity();
        uint256 first = totalSupply + 1;
        if (totalSupply + quantity > MAX_SUPPLY) revert SoldOut();
        if (mintedBy[msg.sender] + quantity > maxPerWallet) revert WalletLimit();
        if (msg.value != price * quantity) revert WrongPayment();

        mintedBy[msg.sender] += quantity;
        totalSupply += quantity;
        for (uint256 i; i < quantity; ++i) {
            _mint(msg.sender, first + i);
        }
        emit Minted(msg.sender, first, quantity);
    }

    /// @notice Owner can reserve some balloons (team / giveaways), outside the wallet limit.
    function ownerMint(address to, uint256 quantity) external onlyOwner {
        uint256 first = totalSupply + 1;
        if (totalSupply + quantity > MAX_SUPPLY) revert SoldOut();
        totalSupply += quantity;
        for (uint256 i; i < quantity; ++i) {
            _mint(to, first + i);
        }
        emit Minted(to, first, quantity);
    }

    // ------------------------------------------------------------ metadata
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        _requireOwned(tokenId);
        return string.concat(_baseTokenURI, tokenId.toString(), ".json");
    }

    function contractURI() external view returns (string memory) {
        return string.concat(_baseTokenURI, "collection.json");
    }

    // ------------------------------------------------------------ admin
    function setMintOpen(bool open) external onlyOwner { mintOpen = open; }
    function setPrice(uint256 newPrice) external onlyOwner { price = newPrice; }
    function setMaxPerWallet(uint256 n) external onlyOwner { maxPerWallet = n; }
    function setBaseURI(string calldata uri) external onlyOwner { _baseTokenURI = uri; }
    function setRoyalty(address receiver, uint96 bps) external onlyOwner { _setDefaultRoyalty(receiver, bps); }

    function withdraw(address payable to) external onlyOwner {
        (bool ok, ) = to.call{value: address(this).balance}("");
        if (!ok) revert WithdrawFailed();
    }

    function supportsInterface(bytes4 id) public view override(ERC721, ERC2981) returns (bool) {
        return super.supportsInterface(id);
    }
}
