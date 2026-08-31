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
- [ ] README.md
- [ ] google.md
- [ ] meta.md
- [ ] amazon.md
- [ ] microsoft.md
- [ ] netflix.md
- [ ] apple.md
- [ ] ai_startups_and_labs.md

## 02_dsa_and_coding/
- [ ] README.md
- [ ] coding_interview_framework.md
- patterns/ (each of the 16 below gets: concept.md, template.py, common_mistakes.md, communication_tips.md, problem_tracker.md, solutions/.gitkeep)
  - [ ] 01_arrays_and_hashing
  - [ ] 02_two_pointers
  - [ ] 03_sliding_window
  - [ ] 04_stack_and_monotonic_stack
  - [ ] 05_linked_lists
  - [ ] 06_binary_search
  - [ ] 07_intervals
  - [ ] 08_trees_and_bsts
  - [ ] 09_heaps_and_priority_queues
  - [ ] 10_graphs
  - [ ] 11_backtracking
  - [ ] 12_greedy
  - [ ] 13_dynamic_programming
  - [ ] 14_tries
  - [ ] 15_bit_manipulation
  - [ ] 16_recursion_and_complexity

## 03_python_core_and_advanced/
- [ ] README.md
- [ ] 01_data_model_and_object_references.md
- [ ] 02_mutable_vs_immutable.md
- [ ] 03_shallow_vs_deep_copy.md
- [ ] 04_functions_args_kwargs.md
- [ ] 05_closures_and_decorators.md
- [ ] 06_iterators_and_generators.md
- [ ] 07_context_managers.md
- [ ] 08_exceptions_and_error_handling.md
- [ ] 09_type_hints_and_mypy.md
- [ ] 10_oop_solid_composition_vs_inheritance.md
- [ ] 11_dataclasses_and_pydantic.md
- [ ] 12_performance_and_profiling.md
- [ ] 13_gil_threading_multiprocessing_asyncio.md
- [ ] 14_memory_management_and_gc.md
- [ ] 15_testing_pytest_mocking_fixtures.md
- [ ] 16_logging_and_observability.md
- [ ] 17_clean_code_and_project_structure.md

## 04_sql_and_databases/
- [ ] README.md
- [ ] 01_sql_fundamentals.md
- [ ] 02_joins.md
- [ ] 03_aggregations.md
- [ ] 04_ctes.md
- [ ] 05_window_functions.md
- [ ] 06_subqueries.md
- [ ] 07_indexes_and_query_optimization.md
- [ ] 08_transactions_and_acid.md
- [ ] 09_isolation_levels_locks_and_deadlocks.md
- [ ] 10_normalization_and_denormalization.md
- [ ] 11_postgresql_specific_concepts.md
- [ ] 12_schema_design.md
- [ ] 13_data_migration_strategies.md
- [ ] 14_orm_tradeoffs_and_django_orm_optimization.md
- [ ] sql_practice_questions.md
- [ ] sql_query_patterns.md
- [ ] database_troubleshooting_scenarios.md
- [ ] postgresql_interview_qna.md

## 05_backend_engineering/
- [ ] README.md
- [ ] 01_rest_api_design.md
- [ ] 02_api_versioning.md
- [ ] 03_auth_jwt_oauth_rbac.md
- [ ] 04_pagination_filtering_sorting_search.md
- [ ] 05_rate_limiting.md
- [ ] 06_caching_with_redis.md
- [ ] 07_background_tasks_celery_queues.md
- [ ] 08_file_upload_and_async_processing.md
- [ ] 09_idempotency_and_retries.md
- [ ] 10_webhooks.md
- [ ] 11_api_gateways.md
- [ ] 12_microservices_vs_monolith.md
- [ ] 13_docker_and_containerization.md
- [ ] 14_ci_cd_basics.md
- [ ] 15_security_owasp_validation_secrets_cors_csrf.md
- [ ] 16_monitoring_logging_metrics_tracing.md
- [ ] 17_django_and_drf_patterns.md
- [ ] 18_elasticsearch_and_search_basics.md
- [ ] real_backend_interview_scenarios.md

## 06_system_design/
- [ ] README.md
- fundamentals/
  - [ ] requirement_clarification.md
  - [ ] capacity_estimation.md
  - [ ] api_design.md
  - [ ] data_modeling.md
  - [ ] caching.md
  - [ ] load_balancing.md
  - [ ] database_replication_and_sharding.md
  - [ ] queues_and_event_driven_systems.md
  - [ ] consistency_and_availability_tradeoffs.md
  - [ ] reliability_fault_tolerance_observability_security.md
- exercises/
  - [ ] url_shortener.md
  - [ ] rate_limiter.md
  - [ ] notification_system.md
  - [ ] file_storage_and_upload_service.md
  - [ ] pdf_ocr_processing_pipeline.md
  - [ ] payment_invoice_system.md
  - [ ] search_autocomplete_service.md
  - [ ] chat_messaging_system.md
  - [ ] job_queue_system.md
  - [ ] api_gateway.md
  - [ ] feature_flag_system.md

## 07_low_level_design/
- [ ] README.md
- fundamentals/
  - [ ] oop_design.md
  - [ ] solid_principles.md
  - [ ] design_patterns.md
  - [ ] uml_class_diagrams_mermaid.md
  - [ ] thread_safety_and_concurrency.md
  - [ ] extensible_code_design.md
- exercises/
  - [ ] parking_lot.md
  - [ ] elevator.md
  - [ ] library_management.md
  - [ ] splitwise.md
  - [ ] cache.md
  - [ ] rate_limiter.md
  - [ ] notification_service.md
  - [ ] payment_workflow.md

## 08_ai_ml_nlp/
- [ ] README.md
- [ ] 01_core_ml_concepts.md
- [ ] 02_data_preprocessing_and_feature_engineering.md
- [ ] 03_model_training_and_inference_fundamentals.md
- [ ] 04_numpy_pandas_sklearn_concepts.md
- [ ] 05_nlp_basics_tokenization_embeddings_transformers_attention.md

## 09_ai_backend_and_llm_systems/
- [ ] README.md
- [ ] 01_vector_databases_and_similarity_search.md
- [ ] 02_rag_system_architecture.md
- [ ] 03_prompt_engineering_fundamentals.md
- [ ] 04_llm_api_integration.md
- [ ] 05_streaming_responses.md
- [ ] 06_model_evaluation.md
- [ ] 07_hallucination_mitigation.md
- [ ] 08_guardrails_and_content_safety.md
- [ ] 09_embedding_pipelines.md
- [ ] 10_chunking_strategies.md
- [ ] 11_retrieval_and_reranking.md
- [ ] 12_llm_observability.md
- [ ] 13_cost_latency_throughput_batching_caching.md
- [ ] 14_ai_data_privacy_and_pii_handling.md
- [ ] 15_model_serving_architecture.md
- [ ] 16_fine_tuning_vs_rag_tradeoffs.md
- [ ] 17_agent_and_workflow_basics.md
- mini_projects/
  - [ ] rag_document_qa_api.md
  - [ ] resume_search_using_embeddings.md
  - [ ] pdf_extraction_ocr_rag_pipeline.md
  - [ ] ai_support_ticket_classification.md
  - [ ] llm_powered_api_doc_assistant.md
  - [ ] semantic_search_pgvector_or_elasticsearch.md

## 10_projects_and_resume/
- [ ] README.md
- [ ] faang_maang_resume_template.md
- [ ] ai_backend_resume_template.md
- [ ] linkedin_headline_and_about.md
- [ ] github_project_readme_template.md
- [ ] project_architecture_explanation_template.md
- [ ] star_format_project_stories.md
- [ ] project_deep_dive_template.md
- sample_storytelling/
  - [ ] django_rest_apis.md
  - [ ] postgresql.md
  - [ ] elasticsearch.md
  - [ ] ocr_pdf_processing.md
  - [ ] docker.md
  - [ ] microservices.md
  - [ ] api_gateway_design.md

## 11_behavioral_and_leadership/
- [ ] README.md
- [ ] star_method_guide.md
- [ ] amazon_leadership_principles_story_bank.md
- [ ] google_meta_style_behavioral_questions.md
- [ ] conflict_resolution_questions.md
- [ ] failure_and_learning_questions.md
- [ ] ownership_and_leadership_questions.md
- [ ] project_collaboration_questions.md
- [ ] why_this_company_template.md
- [ ] tell_me_about_yourself_template.md
- [ ] salary_and_notice_period_templates.md
- [ ] story_bank_tracker.md

## 12_mock_interviews/
- [ ] README.md
- [ ] coding_mock_interview_template.md
- [ ] system_design_mock_interview_template.md
- [ ] behavioral_mock_interview_template.md
- [ ] interview_feedback_rubric.md
- [ ] weakness_tracker.md
- [ ] mistake_log.md

## 13_job_application_tracking/
- [ ] README.md
- [ ] company_application_tracker.md
- [ ] problem_solving_progress_tracker.md
- [ ] weekly_scorecard.md

## 14_resources/
- [ ] README.md
- [ ] books_and_courses.md
- [ ] youtube_channels_and_blogs.md
- [ ] practice_platforms.md
- [ ] useful_github_repos.md
- [ ] cheat_sheets_index.md

## 15_progress_tracking/
- [ ] README.md
- [ ] overall_progress_dashboard.md
- [ ] skills_self_assessment.md
- [ ] twelve_week_progress_log.md

---
Total: ~290 files. Checkboxes updated as batches complete and are independently verified.
