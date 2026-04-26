def test_sim_kernel_can_import_contracts_without_packs() -> None:
    import fw_contracts
    import fos_sim_kernel

    assert fw_contracts.CONTRACTS_VERSION == "0.1.0"
    assert fos_sim_kernel.__version__ == "0.1.0"
