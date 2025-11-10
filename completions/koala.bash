#!/usr/bin/env bash
# Bash completion script for Koala's Forge CLI
# Installation: source this file or copy to /etc/bash_completion.d/

_koala_completion() {
    local cur prev opts base
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="install update uninstall list search categories info preset batch export compare import rollback plugin sync events status version health config doctor cleanup"

    # Command aliases
    local aliases="i u upgrade remove rm r ls s find show log st v"

    # All commands including aliases
    local all_commands="$commands $aliases"

    # Flags
    local global_flags="--help -h --version -v"
    local install_flags="-y --dry-run -s --sequential -f --force"
    local update_flags="-y --all"
    local list_flags="--installed --category"
    local rollback_flags="list create restore"
    local plugin_flags="list load reload"
    local sync_flags="status push pull"
    local config_flags="show get set init"
    local doctor_flags="--fix"
    local cleanup_flags="--keep --dry-run"
    local export_flags="--format"

    # If we're completing the first argument (command)
    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "${all_commands}" -- ${cur}) )
        return 0
    fi

    # Get the main command (handle aliases)
    local command="${COMP_WORDS[1]}"
    case "$command" in
        i) command="install" ;;
        u|upgrade) command="update" ;;
        remove|rm|r) command="uninstall" ;;
        ls) command="list" ;;
        s|find) command="search" ;;
        cat) command="categories" ;;
        show) command="info" ;;
        log) command="events" ;;
        st) command="status" ;;
        v) command="version" ;;
    esac

    # Complete based on the command
    case "$command" in
        install)
            case "$prev" in
                install|i)
                    COMPREPLY=( $(compgen -W "${install_flags}" -- ${cur}) )
                    ;;
                *)
                    # Complete with package names
                    if [[ ${cur} == -* ]]; then
                        COMPREPLY=( $(compgen -W "${install_flags}" -- ${cur}) )
                    fi
                    ;;
            esac
            ;;

        update)
            COMPREPLY=( $(compgen -W "${update_flags}" -- ${cur}) )
            ;;

        list)
            case "$prev" in
                --category)
                    local categories="ai_local development_core development_tools databases containers cloud_tools terminal_tools security productivity communication browsers gaming creative audio"
                    COMPREPLY=( $(compgen -W "${categories}" -- ${cur}) )
                    ;;
                *)
                    COMPREPLY=( $(compgen -W "${list_flags}" -- ${cur}) )
                    ;;
            esac
            ;;

        preset)
            if [ $COMP_CWORD -eq 2 ]; then
                local presets="list ai-developer full-stack-developer data-scientist creative-professional system-administrator"
                COMPREPLY=( $(compgen -W "${presets}" -- ${cur}) )
            fi
            ;;

        export)
            case "$prev" in
                --format)
                    COMPREPLY=( $(compgen -W "txt json yaml" -- ${cur}) )
                    ;;
                *)
                    COMPREPLY=( $(compgen -W "${export_flags}" -- ${cur}) )
                    ;;
            esac
            ;;

        rollback)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "${rollback_flags}" -- ${cur}) )
            fi
            ;;

        plugin)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "${plugin_flags}" -- ${cur}) )
            fi
            ;;

        sync)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "${sync_flags}" -- ${cur}) )
            fi
            ;;

        config)
            case "$prev" in
                config)
                    COMPREPLY=( $(compgen -W "${config_flags}" -- ${cur}) )
                    ;;
                get|set)
                    local config_keys="parallel_downloads cache_retention notification_enabled auto_update_check log_level"
                    COMPREPLY=( $(compgen -W "${config_keys}" -- ${cur}) )
                    ;;
            esac
            ;;

        doctor)
            COMPREPLY=( $(compgen -W "${doctor_flags}" -- ${cur}) )
            ;;

        cleanup)
            case "$prev" in
                --keep)
                    # No completion for numbers
                    return 0
                    ;;
                *)
                    COMPREPLY=( $(compgen -W "${cleanup_flags}" -- ${cur}) )
                    ;;
            esac
            ;;

        batch|compare|import)
            # Complete with file names
            COMPREPLY=( $(compgen -f -- ${cur}) )
            ;;
    esac
}

# Register the completion function
complete -F _koala_completion koala
complete -F _koala_completion ./koala
