# MANIFEST — faang_maang_ai_interview_prep

Authoritative file inventory. Used to track build progress and for final verification. Do not
rename, skip, or add files outside this list without updating it here first.

## Root
- [x] README.md
- [x] .gitignore
- [x] STYLE_GUIDE.md
- [x] MANIFEST.md (this file)

## 00_master_plan/
- [x] README.md
- [x] 12_week_plan.md
- [x] start_here_first_7_days.md
- [x] daily_checklist.md
- [x] weekly_review.md
- [x] priority_topics.md
- [x] revision_schedule.md
- [x] mock_interview_schedule.md

## 01_company_interview_patterns/
- [x] README.md
- [x] google.md
- [x] meta.md
- [x] amazon.md
- [x] microsoft.md
- [x] netflix.md
- [x] apple.md
- [x] ai_startups_and_labs.md

## 02_dsa_and_coding/
- [x] README.md
- [x] coding_interview_framework.md
- patterns/ (each of the 16 below gets: concept.md, template.py, common_mistakes.md, communication_tips.md, problem_tracker.md, solutions/.gitkeep)
  - [x] 01_arrays_and_hashing
  - [x] 02_two_pointers
  - [x] 03_sliding_window
  - [x] 04_stack_and_monotonic_stack
  - [x] 05_linked_lists
  - [x] 06_binary_search
  - [x] 07_intervals
  - [x] 08_trees_and_bsts
  - [x] 09_heaps_and_priority_queues
  - [x] 10_graphs
  - [x] 11_backtracking
  - [x] 12_greedy
  - [x] 13_dynamic_programming
  - [x] 14_tries
  - [x] 15_bit_manipulation
  - [x] 16_recursion_and_complexity

## 03_python_core_and_advanced/
- [x] README.md
- [x] 01_data_model_and_object_references.md
- [x] 02_mutable_vs_immutable.md
- [x] 03_shallow_vs_deep_copy.md
- [x] 04_functions_args_kwargs.md
- [x] 05_closures_and_decorators.md
- [x] 06_iterators_and_generators.md
- [x] 07_context_managers.md
- [x] 08_exceptions_and_error_handling.md
- [x] 09_type_hints_and_mypy.md
- [x] 10_oop_solid_composition_vs_inheritance.md
- [x] 11_dataclasses_and_pydantic.md
- [x] 12_performance_and_profiling.md
- [x] 13_gil_threading_multiprocessing_asyncio.md
- [x] 14_memory_management_and_gc.md
- [x] 15_testing_pytest_mocking_fixtures.md
- [x] 16_logging_and_observability.md
- [x] 17_clean_code_and_project_structure.md

## 04_sql_and_databases/
- [x] README.md
- [x] 01_sql_fundamentals.md
- [x] 02_joins.md
- [x] 03_aggregations.md
- [x] 04_ctes.md
- [x] 05_window_functions.md
- [x] 06_subqueries.md
- [x] 07_indexes_and_query_optimization.md
- [x] 08_transactions_and_acid.md
- [x] 09_isolation_levels_locks_and_deadlocks.md
- [x] 10_normalization_and_denormalization.md
- [x] 11_postgresql_specific_concepts.md
- [x] 12_schema_design.md
- [x] 13_data_migration_strategies.md
- [x] 14_orm_tradeoffs_and_django_orm_optimization.md
- [x] sql_practice_questions.md
- [x] sql_query_patterns.md
- [x] database_troubleshooting_scenarios.md
- [x] postgresql_interview_qna.md

## 05_backend_engineering/
- [x] README.md
- [x] 01_rest_api_design.md
- [x] 02_api_versioning.md
- [x] 03_auth_jwt_oauth_rbac.md
- [x] 04_pagination_filtering_sorting_search.md
- [x] 05_rate_limiting.md
- [x] 06_caching_with_redis.md
- [x] 07_background_tasks_celery_queues.md
- [x] 08_file_upload_and_async_processing.md
- [x] 09_idempotency_and_retries.md
- [x] 10_webhooks.md
- [x] 11_api_gateways.md
- [x] 12_microservices_vs_monolith.md
- [x] 13_docker_and_containerization.md
- [x] 14_ci_cd_basics.md
- [x] 15_security_owasp_validation_secrets_cors_csrf.md
- [x] 16_monitoring_logging_metrics_tracing.md
- [x] 17_django_and_drf_patterns.md
- [x] 18_elasticsearch_and_search_basics.md
- [x] real_backend_interview_scenarios.md

## 06_system_design/
- [x] README.md
- fundamentals/
  - [x] requirement_clarification.md
  - [x] capacity_estimation.md
  - [x] api_design.md
  - [x] data_modeling.md
  - [x] caching.md
  - [x] load_balancing.md
  - [x] database_replication_and_sharding.md
  - [x] queues_and_event_driven_systems.md
  - [x] consistency_and_availability_tradeoffs.md
  - [x] reliability_fault_tolerance_observability_security.md
- exercises/
  - [x] url_shortener.md
  - [x] rate_limiter.md
  - [x] notification_system.md
  - [x] file_storage_and_upload_service.md
  - [x] pdf_ocr_processing_pipeline.md
  - [x] payment_invoice_system.md
  - [x] search_autocomplete_service.md
  - [x] chat_messaging_system.md
  - [x] job_queue_system.md
  - [x] api_gateway.md
  - [x] feature_flag_system.md

## 07_low_level_design/
- [x] README.md
- fundamentals/
  - [x] oop_design.md
  - [x] solid_principles.md
  - [x] design_patterns.md
  - [x] uml_class_diagrams_mermaid.md
  - [x] thread_safety_and_concurrency.md
  - [x] extensible_code_design.md
- exercises/
  - [x] parking_lot.md
  - [x] elevator.md
  - [x] library_management.md
  - [x] splitwise.md
  - [x] cache.md
  - [x] rate_limiter.md
  - [x] notification_service.md
  - [x] payment_workflow.md

## 08_ai_ml_nlp/
- [x] README.md
- [x] 01_core_ml_concepts.md
- [x] 02_data_preprocessing_and_feature_engineering.md
- [x] 03_model_training_and_inference_fundamentals.md
- [x] 04_numpy_pandas_sklearn_concepts.md
- [x] 05_nlp_basics_tokenization_embeddings_transformers_attention.md

## 09_ai_backend_and_llm_systems/
- [x] README.md
- [x] 01_vector_databases_and_similarity_search.md
- [x] 02_rag_system_architecture.md
- [x] 03_prompt_engineering_fundamentals.md
- [x] 04_llm_api_integration.md
- [x] 05_streaming_responses.md
- [x] 06_model_evaluation.md
- [x] 07_hallucination_mitigation.md
- [x] 08_guardrails_and_content_safety.md
- [x] 09_embedding_pipelines.md
- [x] 10_chunking_strategies.md
- [x] 11_retrieval_and_reranking.md
- [x] 12_llm_observability.md
- [x] 13_cost_latency_throughput_batching_caching.md
- [x] 14_ai_data_privacy_and_pii_handling.md
- [x] 15_model_serving_architecture.md
- [x] 16_fine_tuning_vs_rag_tradeoffs.md
- [x] 17_agent_and_workflow_basics.md
- mini_projects/
  - [x] rag_document_qa_api.md
  - [x] resume_search_using_embeddings.md
  - [x] pdf_extraction_ocr_rag_pipeline.md
  - [x] ai_support_ticket_classification.md
  - [x] llm_powered_api_doc_assistant.md
  - [x] semantic_search_pgvector_or_elasticsearch.md

## 10_projects_and_resume/
- [x] README.md
- [x] faang_maang_resume_template.md
- [x] ai_backend_resume_template.md
- [x] linkedin_headline_and_about.md
- [x] github_project_readme_template.md
- [x] project_architecture_explanation_template.md
- [x] star_format_project_stories.md
- [x] project_deep_dive_template.md
- sample_storytelling/
  - [x] django_rest_apis.md
  - [x] postgresql.md
  - [x] elasticsearch.md
  - [x] ocr_pdf_processing.md
  - [x] docker.md
  - [x] microservices.md
  - [x] api_gateway_design.md

## 11_behavioral_and_leadership/
- [x] README.md
- [x] star_method_guide.md
- [x] amazon_leadership_principles_story_bank.md
- [x] google_meta_style_behavioral_questions.md
- [x] conflict_resolution_questions.md
- [x] failure_and_learning_questions.md
- [x] ownership_and_leadership_questions.md
- [x] project_collaboration_questions.md
- [x] why_this_company_template.md
- [x] tell_me_about_yourself_template.md
- [x] salary_and_notice_period_templates.md
- [x] story_bank_tracker.md

## 12_mock_interviews/
- [x] README.md
- [x] coding_mock_interview_template.md
- [x] system_design_mock_interview_template.md
- [x] behavioral_mock_interview_template.md
- [x] interview_feedback_rubric.md
- [x] weakness_tracker.md
- [x] mistake_log.md

## 13_job_application_tracking/
- [x] README.md
- [x] company_application_tracker.md
- [x] problem_solving_progress_tracker.md
- [x] weekly_scorecard.md

## 14_resources/
- [x] README.md
- [x] books_and_courses.md
- [x] youtube_channels_and_blogs.md
- [x] practice_platforms.md
- [x] useful_github_repos.md
- [x] cheat_sheets_index.md

## 15_progress_tracking/
- [x] README.md
- [x] overall_progress_dashboard.md
- [x] skills_self_assessment.md
- [x] twelve_week_progress_log.md

---
Total: ~290 files. Checkboxes updated as batches complete and are independently verified.
